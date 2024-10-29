import json
import yfinance as yf
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta, date
from users.models import UserStock  # Import the UserStock model
from .models import ETFHolding  # Import the ETFHolding model
from django.contrib.auth.decorators import login_required # User authorization
from django.utils import timezone
from decimal import Decimal
from django.contrib import messages
from prophet import Prophet
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from .forms import TradeStockForm
from users.models import Profile, UserStock, StockTransaction  # Make sure to import Profile

# Constants for date range
START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

# Require users to be logged into an account to see their dashboard
@login_required(login_url='/users/login_user')
def dashboard(request):
    profile = request.user.profile
    available_cash = profile.available_cash  # Get available cash
    # Get all stocks for the logged-in user
    user_stocks = UserStock.objects.filter(profile=request.user.profile)

    # Prepare data for the chart (convert to list of dictionaries)
    stock_data = [
        {
            'name': stock.company_name,
            'price': float(stock.stock_price),  # Ensure stock_price is float for JSON serialization
            'quantity': float(stock.stock_quantity)
        }
        for stock in user_stocks
    ]

    # Render the dashboard template with the user's stocks, available cash
    return render(request, 'dashboard/dashboard.html', {
        'available_cash': available_cash,
        'user_stocks': user_stocks,
        'stock_data': json.dumps(stock_data),
    })

@login_required(login_url='/users/login_user')
def live_update(request):
    # Get the current user's profile
    profile = request.user.profile
    
    # Get all the stocks the user owns
    user_stocks = UserStock.objects.filter(profile=profile)
    # Get the cash available for the user (assuming this is part of the Profile model)
    available_cash = profile.available_cash  # Get available cash

    total_stock_value = Decimal(0)  # To accumulate the total value of all stocks
    stock_data_dict = {} # To store the price and quantity of each stock owned

    # Loop through each stock to update its value based on the current market price
    for stock in user_stocks:
        stock_data = yf.Ticker(stock.company_name)
        data = stock_data.info

        # Get the current stock price
        if data.get('quoteType') in ['MUTUALFUND', 'ETF']:
            current_price = Decimal(data.get('previousClose', 0))  # For ETFs/mutual funds, use previous close
        else:
            current_price = Decimal(data.get('currentPrice', data.get('ask', data.get('regularMarketPrice', 0))))  # For stocks, use current price

        # Calculate total value of this stock (quantity * current price)
        stock_value = stock.stock_quantity * current_price
        total_stock_value += stock_value  # Add the stock value to the total

        stock_data_dict[stock.company_name] = { # Store the current price and quantity into the dict to call in the html
            'price': float(current_price),
            'quantity': float(stock.stock_quantity),
        }

    # Update the total portfolio value in the user's profile
    profile.total_stock_value = total_stock_value
    profile.total_value = available_cash + total_stock_value  # Total value = cash + stock value
    profile.save()  # Save the updated profile
    
    # Return both the available cash and total portfolio value
    return JsonResponse({
        'available_cash': float(available_cash),
        'total_value': float(profile.total_value),
        'total_stock_value': float(total_stock_value), #Grabbing this one
        'stock_data_dict': stock_data_dict
    })

# Function to scrape ETF holdings
def fetch_etf_holdings(etf_symbol):
    # print("Fetching ETF holdings for:", etf_symbol)
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode

    # Automatically manage ChromeDriver with webdriver_manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Open Yahoo Finance ETF holdings page
        driver.get(f"https://finance.yahoo.com/quote/{etf_symbol}/holdings")
        driver.implicitly_wait(5)

        try:
            # Find top holdings section
            holdings_section = driver.find_element(By.XPATH, '//*[@data-testid="top-holdings"]')
            percents = holdings_section.find_elements(By.CSS_SELECTOR, 'span.data.yf-1ix710n')
            holdings = holdings_section.find_elements(By.CSS_SELECTOR, 'a')

            # Store the top 10 holdings and percentages
            etf_holdings = []
            for holding, percent in zip(holdings, percents):
                holding_name = holding.text.strip()
                holding_percent = float(percent.text.strip().replace('%', '')) / 100  # Convert to decimal
                holding_symbol = holding.get_attribute("href").split("/")[-1]  # Get the stock symbol from URL

                etf_holdings.append({
                    'name': holding_name,
                    'percent': holding_percent,
                    'symbol': holding_symbol
                })

            return etf_holdings[:10]  # Return top 10 holdings

        except Exception as e:
            print("Error locating holdings section:", e)
            return []
    finally:
        driver.quit()

@login_required(login_url='/users/login_user')
def assetCalc(request):
    if request.method == 'POST':
        #print("Here I am")
        etf_symbol = request.POST.get('etf').upper()  # Get the ETF symbol from the form
        stocks_owned = request.POST.get('stocksOwned').split(',')  # Get stocks owned
        
        # Fetch ETF data using yfinance
        etf_data = yf.Ticker(etf_symbol)
        etf_info = etf_data.info  # Get ETF information

        # Check if the ETF symbol is valid and not delisted
        if 'symbol' not in etf_info or 'delisted' in etf_info.get('status', '').lower():
            messages.error(request, f"Invalid or delisted ETF symbol: {etf_symbol}. Please enter a valid ETF symbol.")
            return redirect('assetCalc')  # Redirect to the assetCalc view or your desired page
        
        # Check for existing ETF holdings in the database
        existing_holdings = ETFHolding.objects.filter(etf_ticker=etf_symbol)
        
        if existing_holdings.exists():
            # Check if the existing holdings were updated in the last week
            # Calculate the cutoff for one week ago with timezone awareness
            week_ago = timezone.now() - timedelta(weeks=1)
        
            if all(holding.last_updated > week_ago for holding in existing_holdings):
                # If holdings exist, retrieve them and return to the template
                etf_price = Decimal(yf.Ticker(etf_symbol).history(period='1d')['Close'].iloc[0])  # Get the ETF price
                calculated_holdings = []
                for holding in existing_holdings:
                    holding_value_in_etf = (Decimal(holding.holding_percentage) / Decimal(100) * 
                                            Decimal(yf.Ticker(etf_symbol).history(period='1d')['Close'].iloc[0]) * 
                                            Decimal(Decimal(stocks_owned[0])))  # Calculate holding value
                    stock_price = Decimal(yf.Ticker(holding.stock_symbol).history(period='1d')['Close'].iloc[0])  # Get stock price
                    stock_owned = holding_value_in_etf / stock_price  # Calculate amount owned

                    calculated_holdings.append({
                        'stock_symbol': holding.stock_symbol,
                        'holding_percentage': holding.holding_percentage,
                        'holding_value_in_etf': holding_value_in_etf,
                        'stock_price': stock_price,
                        'stock_owned': stock_owned
                    })
                return render(request, 'dashboard/assetCalc.html', {
                    'etf_symbol': etf_symbol,
                    'calculated_holdings': calculated_holdings,
                    'etf_price': etf_price,  # Pass ETF price to template
                    'stocks_owned': float(stocks_owned[0]),
                })
            # Holdings are stale
            else:
                # Filter for stale holdings only (older than a week)
                stale_holdings = existing_holdings.filter(etf_ticker=etf_symbol, last_updated__lt=week_ago)
                # If holdings are stale, delete existing data and proceed to update
                stale_holdings.delete()


        # Fetch ETF holdings using the defined function
        etf_holdings = fetch_etf_holdings(etf_symbol)

        # Initialize the list to hold stock data
        calculated_holdings = []
        
        # Save ETF holdings to the database
        for holding in etf_holdings:
            stock_symbol = holding['name']
            holding_percentage = holding['percent'] * 100  # Convert to percentage
            
            # Create or update ETFHolding instance
            ETFHolding.objects.update_or_create(
                etf_ticker=etf_symbol,  
                stock_symbol=holding['symbol'],
                defaults={
                    'holding_percentage': holding_percentage,
                    'stock_symbol': stock_symbol,  # Store the name as well, if needed
                    'last_updated': datetime.now(),  # Assuming you have a timestamp field
                    'etf_price': etf_data.history(period='1d')['Close'].iloc[0],  # Save the ETF price
                }
            )
        
        for holding in etf_holdings:
            stock_symbol = holding['name']
            holding_percentage = holding['percent'] * 100  # Convert to percentage

            # Calculate the value of the stock based on the ETF shares
            etf_data = yf.Ticker(etf_symbol)
            etf_price = etf_data.history(period='1d')['Close'].iloc[0]  # Get current ETF price
            # print(f"Here is holding percentage: {holding_percentage}, here is ETF price: {etf_price}, here is stocks owned: {stocks_owned}")
            holding_value_in_etf = (holding_percentage / 100) * etf_price * float(stocks_owned[0])  # Calculate value

            # Get stock price of the holding
            stock_data = yf.Ticker(stock_symbol)
            stock_price = stock_data.history(period='1d')['Close'].iloc[0]

            # Calculate the amount of stock owned
            stock_owned = holding_value_in_etf / stock_price

            calculated_holdings.append({
                'stock_symbol': stock_symbol,
                'holding_percentage': holding_percentage,
                'holding_value_in_etf': holding_value_in_etf,
                'stock_price': stock_price,
                'stock_owned': stock_owned,
            })

        return render(request, 'dashboard/assetCalc.html', {
            'etf_symbol': etf_symbol,
            'calculated_holdings': calculated_holdings,
            'etf_price': etf_price,  # Pass ETF price to template
            'stocks_owned': float(stocks_owned[0])
        })

    return render(request, 'dashboard/assetCalc.html', {})


@login_required(login_url='/users/login_user')
def buySell(request):
    profile = request.user.profile
    available_cash = profile.available_cash
    user_stocks = UserStock.objects.filter(profile=profile)
    query = request.session.get('query', None)

    return render(request, 'dashboard/buySell.html', {
        'available_cash': available_cash,
        'user_stocks': user_stocks,
        'company_name': query,
    })
    

@login_required(login_url='/users/login_user')
def execute_trade(request):
    profile = request.user.profile
    available_cash = profile.available_cash
    query = request.session.get('query', None)  # Retrieve 'query' from session
    
    form = TradeStockForm(request.POST)
    
    if request.method == 'POST':
        if form.is_valid():
            trade_type = form.cleaned_data.get('trade_type')  # Safely access cleaned_data
            company_name = query
            stock_quantity = form.cleaned_data.get('stock_quantity')
            order_type = form.cleaned_data.get('order_type')

            # Validate stock_quantity
            if stock_quantity <= 0:
                messages.error(request, "Quantity must be a positive number.")
                return redirect('buySell')
                        
            # Fetch stock data from yfinance
            stock_data = yf.Ticker(company_name)
            data = stock_data.info

            # Validate stock data
            if not data:
                messages.error(request, "Failed to retrieve stock data. Please check the stock symbol.")
                return redirect('buySell')

            # Get stock price
            if data.get('quoteType') in ['MUTUALFUND', 'ETF']:
                stock_price = Decimal(data.get('previousClose', 0))  # For ETFs and mutual funds
            else:
                stock_price = Decimal(data.get('currentPrice', data.get('ask', data.get('regularMarketPrice', 0))))

            if stock_price <= 0:
                messages.error(request, "Invalid stock symbol or stock has been delisted.")
                return redirect('buySell')

            # Calculate total value based on order type
            if order_type == 'shares':
                total_value = stock_quantity * stock_price
            else:  # order_type == 'cash'
                total_value = stock_quantity  # Here, stock_quantity is the cash amount for the order

            is_buy = trade_type == 'buy'

            if is_buy:
                if available_cash >= total_value:
                    # Buy Logic
                    profile.available_cash -= total_value
                    profile.save()

                    user_stock, created = UserStock.objects.get_or_create(
                        profile=profile, company_name=company_name,
                        defaults={'stock_quantity': 0, 'stock_price': stock_price, 'stock_purchase_date': timezone.now()}
                    )
                    # user_stock.stock_quantity += stock_quantity if order_type == 'shares' else total_value / stock_price
                    
                    if order_type == 'shares':
                        user_stock.stock_quantity += stock_quantity
                    else:
                        user_stock.stock_quantity += total_value / stock_price
                            
                    user_stock.save()
                    
                    if order_type == 'shares':
                        StockTransaction.objects.create(
                            profile=profile,
                            company_name=company_name,
                            stock_quantity=stock_quantity,
                            stock_price=stock_price, transaction_type='buy'
                        )
                    else:
                        StockTransaction.objects.create(
                            profile=profile,
                            company_name=company_name,
                            stock_quantity=stock_quantity / stock_price,
                            stock_price=stock_price, transaction_type='buy'
                        )
                        
                    if order_type == 'shares':
                        messages.success(request, f"Successfully bought {stock_quantity:.2f} shares of {company_name}.")
                    else:
                        messages.success(request, f"Successfully bought {stock_quantity / stock_price:.2f} shares of {company_name}.")
                else:
                    messages.error(request, "Not enough cash to buy this stock.")
            else:
                # Sell Logic
                user_stock = UserStock.objects.filter(profile=profile, company_name=company_name).first()
                stock_quantity = stock_quantity / stock_price if order_type == 'cash' else stock_quantity
                
                if user_stock and user_stock.stock_quantity >= stock_quantity:
                    # Calculate total value for selling
                    total_value = stock_quantity * stock_price  # Assuming quantity is the number of shares sold
                    profile.available_cash += total_value
                    profile.save()

                    user_stock.stock_quantity -= stock_quantity
                    if user_stock.stock_quantity == 0:
                        user_stock.delete()
                    else:
                        user_stock.save()

                    StockTransaction.objects.create(
                        profile=profile,
                        company_name=company_name,
                        stock_quantity=stock_quantity,
                        stock_price=stock_price, transaction_type='sell'
                    )
                    messages.success(request, f"Sold {stock_quantity:.2f} shares of {company_name}.")
                else:
                    messages.error(request, "You do not have enough shares to sell.")
        else:
            messages.error(request, "There was an error in your form submission or you entered a value less than 0.02. Please check your inputs.")
    
    return render(request, 'dashboard/buySell.html', {
        'form': form,
        'available_cash': available_cash,
        'user_stocks': UserStock.objects.filter(profile=profile)
    })