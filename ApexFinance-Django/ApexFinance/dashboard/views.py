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
from selenium import webdriver
from prophet import Prophet
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from datetime import date
import pandas as pd
from .forms import TradeStockForm
from users.models import Profile, UserStock, StockTransaction  # Make sure to import Profile

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
            'price': float(stock.stock_price),
            'quantity': float(stock.stock_quantity),
            'total_value': float(stock.stock_quantity * stock.stock_price),
        }
        for stock in user_stocks
    ]

    # Prepare stock_data_dict for each stock to access current price and quantity
    stock_data_dict = {
        stock.company_name: {
            'price': float(stock.stock_price),
            'quantity': float(stock.stock_quantity),
            'total_value': float(stock.stock_quantity * stock.stock_price),
        }
        for stock in user_stocks
    }

    return render(request, 'dashboard/dashboard.html', {
        'available_cash': available_cash,
        'user_stocks': user_stocks,
        'stock_data': json.dumps(stock_data),
        'stock_data_dict': stock_data_dict,  # Add stock_data_dict to context
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
        # Add current stock information to the dictionary
        stock_data_dict[stock.company_name] = {
            'price': float(current_price),
            'quantity': float(stock.stock_quantity),
            'total_value': float(stock_value),
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
        'stock_data': stock_data_dict,
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
        etf_symbols = request.POST.getlist('etf')  # Get the ETF symbols from the form (allowing multiple symbols)
        stocks_owned = request.POST.getlist('stocksOwned')  # Get corresponding stock quantities
        # print(request.POST)  # Debugging line: check what data is being submitted
        print(etf_symbols)
        print(stocks_owned)
        
        # Ensure both lists have the same length
        if len(etf_symbols) != len(stocks_owned):
            messages.error(request, "The number of ETFs and quantities must match.")
            return redirect('assetCalc')

        # Initialize the list to hold calculated holdings for all ETFs
        all_calculated_holdings = []
        combined_holdings = {}  # For aggregating final combined values
        
        for etf_symbol, stocks_owned_qty in zip(etf_symbols, stocks_owned):
            etf_symbol = etf_symbol.upper()  # Ensure the ETF symbol is uppercase
            stocks_owned_qty = float(stocks_owned_qty)  # Convert the quantity to a float
            
            # Fetch ETF data using yfinance
            etf_data = yf.Ticker(etf_symbol)
            etf_info = etf_data.info  # Get ETF information
            

            # Check if the ETF symbol is valid and not delisted
            if 'symbol' not in etf_info or 'delisted' in etf_info.get('status', '').lower():
                messages.error(request, f"Invalid or delisted ETF symbol: {etf_symbol}. Please enter a valid ETF symbol.")
                return redirect('assetCalc')  # Redirect to the assetCalc view or your desired page
            
            # Fetch ETF holdings using the defined function
            etf_holdings = fetch_etf_holdings(etf_symbol)

            # Initialize the list to hold stock data for the current ETF
            calculated_holdings = []

            # Process ETF holdings and calculate stock allocations
            for holding in etf_holdings:
                stock_symbol = holding['name']
                holding_percentage = holding['percent'] * 100  # Convert to percentage
                
                try:
                    etf_history = etf_data.history(period='1d')
                    if not etf_history.empty:
                        etf_price = etf_history['Close'].iloc[0]
                    else:
                        etf_price = None
                        print("No price data available for the ETF.")
                except Exception as e:
                    etf_price = None
                    print(f"An error occurred while fetching ETF price: {e}")
                    
                holding_value_in_etf = (holding_percentage / 100) * etf_price * stocks_owned_qty  # Calculate value

                # Get stock price of the holding
                stock_data = yf.Ticker(stock_symbol)
                print(stock_data)
                stock_price = stock_data.history(period='1d')['Close'].iloc[0]

                # Calculate the amount of stock owned
                stock_owned = holding_value_in_etf / stock_price

                # Append to the ETF-specific list
                calculated_holdings.append({
                    'stock_symbol': stock_symbol,
                    'holding_percentage': holding_percentage,
                    'holding_value_in_etf': holding_value_in_etf,
                    'stock_price': stock_price,
                    'stock_owned': stock_owned,
                })

                # Aggregate into combined holdings
                if stock_symbol not in combined_holdings:
                    combined_holdings[stock_symbol] = {
                        'holding_value': holding_value_in_etf,
                        'stock_owned': stock_owned,
                        'stock_price': stock_price,  # Use the latest stock price encountered
                    }
                else:
                    combined_holdings[stock_symbol]['holding_value'] += holding_value_in_etf
                    combined_holdings[stock_symbol]['stock_owned'] += stock_owned

            # Add the calculated holdings for this ETF to the list
            all_calculated_holdings.append({
                'etf_symbol': etf_symbol,
                'calculated_holdings': calculated_holdings,
                'etf_price': etf_price,  # Pass ETF price to template
                'stocks_owned': stocks_owned_qty,
            })

        # Format combined holdings as a list
        combined_holdings_list = [
            {
                'stock_symbol': stock_symbol,
                'total_holding_value': data['holding_value'],
                'total_stock_owned': data['stock_owned'],
                'stock_price': data['stock_price'],
            }
            for stock_symbol, data in combined_holdings.items()
        ]

        # Return the final render with all ETFs and combined allocations
        return render(request, 'dashboard/assetCalc.html', {
            'all_calculated_holdings': all_calculated_holdings,
            'combined_holdings': combined_holdings_list,
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
    
# Fetch stock data and perform forecasting using Prophet
def fetch_and_forecast(stock, years):
    # Constants for date range
    START = "2010-01-01"
    TODAY = date.today().strftime("%Y-%m-%d")
    
    # Fetch stock data using yfinance
    data = yf.download(stock, START, TODAY)
    if data.empty:
        raise ValueError("Stock not found or data unavailable.")

    data.reset_index(inplace=True)

    # Prepare the data for Prophet
    df_train = data[['Date', 'Close']]
    df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

    # Initialize and fit the Prophet model
    model = Prophet()
    model.fit(df_train)

    # Create future dataframe for predictions
    future = model.make_future_dataframe(periods=years * 365)
    forecast = model.predict(future)

    return data, forecast

@login_required(login_url='/users/login_user')
def stock_forecast_view(request):
    # Get the selected stock and years from the request (defaults are 'MSFT' and 1 year)
    selected_stock = request.GET.get('stock', 'MSFT')
    n_years = int(request.GET.get('years', 1))

    # Fetch stock info using yfinance
    stock_data = yf.Ticker(selected_stock)
    stock_info = stock_data.info
    
     # Get the current stock price
    if stock_info.get('quoteType') in ['MUTUALFUND', 'ETF']:
        is_etf = True
    else:
        is_etf = False

    # Validate the stock symbol
    if 'symbol' not in stock_info or 'delisted' in stock_info.get('status', '').lower():
        messages.error(request, f"Invalid or delisted stock symbol: {selected_stock}. Please enter a valid stock symbol.")
        return redirect('stockPred')

    try:
        # Fetch stock data and forecast
        data, forecast = fetch_and_forecast(selected_stock, n_years)

        # Prepare data for Highcharts.js (raw and forecast data)
        chart_data = {
            'date': data['Date'].astype(str).tolist(),
            'open': data['Open'].tolist(),
            'close': data['Close'].tolist(),
            'forecast_date': forecast['ds'].astype(str).tolist(),
            'forecast_yhat': forecast['yhat'].tolist(),
        }
        
        # Format stock information fields
        formatted_stock_info = {
            'shortName': stock_info.get('shortName', 'N/A'),
            'symbol': stock_info.get('symbol', 'N/A'),
            'currentPrice': stock_info.get('currentPrice', 'N/A'),
            'open': stock_info.get('open', 'N/A'),
            'longName': stock_info.get('longName', 'N/A'),
            'category': stock_info.get('category', 'N/A'),
            'fundFamily': stock_info.get('fundFamily', 'N/A'),
            'previousClose': stock_info.get('previousClose', 'N/A'),
            'currency': stock_info.get('currency', 'N/A'),
            'dayLow': stock_info.get('dayLow', 'N/A'),
            'dayHigh': stock_info.get('dayHigh', 'N/A'),
            'fiftyTwoWeekHigh': stock_info.get('fiftyTwoWeekHigh', 'N/A'),
            'fiftyTwoWeekLow': stock_info.get('fiftyTwoWeekLow', 'N/A'),
            'fiveYearAverageReturn': stock_info.get('fiveYearAverageReturn', 'N/A'),
            'threeYearAverageReturn': stock_info.get('threeYearAverageReturn', 'N/A'),
            'trailingPE': stock_info.get('trailingPE', 'N/A'),
            'trailingAnnualDividendRate': stock_info.get('trailingAnnualDividendRate', 'N/A'),
            'trailingAnnualDividendYield': stock_info.get('trailingAnnualDividendYield', 'N/A'),
            'totalAssets': stock_info.get('totalAssets', 'N/A'),
            'volume': stock_info.get('volume', 'N/A'),
            'exchange': stock_info.get('exchange', 'N/A'),
            'fundInceptionDate': stock_info.get('fundInceptionDate', 'N/A'),
            'beta3Year': stock_info.get('beta3Year', 'N/A'),
            'averageDailyVolume10Day': stock_info.get('averageDailyVolume10Day', 'N/A'),
            'marketCap': stock_info.get('marketCap', 'N/A'),
            'sector': stock_info.get('sector', 'N/A'),
            'industry': stock_info.get('industry', 'N/A'),
            '52WeekChange': stock_info.get('52WeekChange', 'N/A'),
            'dividendYield': stock_info.get('dividendYield', 'N/A'),
            'forwardPE': stock_info.get('forwardPE', 'N/A'), 
            'forwardEps': stock_info.get('forwardEps', 'N/A'),
            'beta': stock_info.get('beta', 'N/A'),
            'averageVolume': stock_info.get('averageVolume', 'N/A'),
            'dayLow': stock_info.get('dayLow', 'N/A'),
            'dayHigh': stock_info.get('dayHigh', 'N/A'),
            'floatShares': stock_info.get('floatShares', 'N/A'),
            'dividendRate': stock_info.get('dividendRate', 'N/A'),
            'earningsGrowth': stock_info.get('earningsGrowth', 'N/A'),
        }
        
        # Ensure 'fundInceptionDate' is not 'N/A' and convert it to an integer if possible
        timestamp = formatted_stock_info.get('fundInceptionDate', 'N/A')

        # Check if the timestamp is a valid integer before processing
        if timestamp != 'N/A':
            try:
                timestamp = int(timestamp)  # Ensure timestamp is an integer
                date = datetime.fromtimestamp(timestamp)  # Convert Unix timestamp to datetime object
                formatted_date = date.strftime('%m/%d/%Y')  # Format the date as MM/DD/YYYY
                formatted_stock_info['fundInceptionDate'] = formatted_date  # Update the formatted date in the dictionary
            except (ValueError, TypeError):
                formatted_stock_info['fundInceptionDate'] = 'Invalid Date'  # Handle cases where conversion fails
        else:
            formatted_stock_info['fundInceptionDate'] = 'N/A'  # If no valid timestamp, keep it as N/A

        # Turns it into comma string (e.g, x,xxx,xxx,xxx)
        formatted_stock_info['marketCap'] = '{:,}'.format(formatted_stock_info['marketCap']) if isinstance(formatted_stock_info['marketCap'], int) else formatted_stock_info['marketCap']
        formatted_stock_info['averageVolume'] = '{:,}'.format(formatted_stock_info['averageVolume']) if isinstance(formatted_stock_info['averageVolume'], int) else formatted_stock_info['averageVolume']
        formatted_stock_info['floatShares'] = '{:,}'.format(formatted_stock_info['floatShares']) if isinstance(formatted_stock_info['floatShares'], int) else formatted_stock_info['floatShares']
        formatted_stock_info['volume'] = '{:,}'.format(formatted_stock_info['volume']) if isinstance(formatted_stock_info['volume'], int) else formatted_stock_info['volume']
        formatted_stock_info['totalAssets'] = '{:,}'.format(formatted_stock_info['totalAssets']) if isinstance(formatted_stock_info['totalAssets'], int) else formatted_stock_info['totalAssets']
        formatted_stock_info['averageDailyVolume10Day'] = '{:,}'.format(formatted_stock_info['averageDailyVolume10Day']) if isinstance(formatted_stock_info['averageDailyVolume10Day'], int) else formatted_stock_info['averageDailyVolume10Day']
    
        # Turns it into percents %
        formatted_stock_info['dividendYield'] = f"{(formatted_stock_info['dividendYield'] * 100):.2f}%" if isinstance(formatted_stock_info['dividendYield'], (int, float)) else formatted_stock_info['dividendYield']
        formatted_stock_info['earningsGrowth'] = f"{(formatted_stock_info['earningsGrowth'] * 100):.2f}%" if isinstance(formatted_stock_info['earningsGrowth'], (int, float)) else formatted_stock_info['earningsGrowth']
        formatted_stock_info['trailingAnnualDividendYield'] = f"{(formatted_stock_info['trailingAnnualDividendYield'] * 100):.2f}%" if isinstance(formatted_stock_info['trailingAnnualDividendYield'], (int, float)) else formatted_stock_info['trailingAnnualDividendYield']
        formatted_stock_info['52WeekChange'] = f"{(formatted_stock_info['52WeekChange'] * 100):.2f}%" if isinstance(formatted_stock_info['52WeekChange'], (int, float)) else formatted_stock_info['52WeekChange']
        formatted_stock_info['fiveYearAverageReturn'] = f"{(formatted_stock_info['fiveYearAverageReturn'] * 100):.2f}%" if isinstance(formatted_stock_info['fiveYearAverageReturn'], (int, float)) else formatted_stock_info['fiveYearAverageReturn']
        formatted_stock_info['threeYearAverageReturn'] = f"{(formatted_stock_info['threeYearAverageReturn'] * 100):.2f}%" if isinstance(formatted_stock_info['threeYearAverageReturn'], (int, float)) else formatted_stock_info['threeYearAverageReturn']

        context = {
            'selected_stock': selected_stock,
            'stock_info': formatted_stock_info,
            'chart_data': chart_data,
            'forecast': forecast[['ds', 'yhat']].tail(10).to_dict(orient='records'),
            'is_etf': is_etf,
        }

        return render(request, 'dashboard/stockPred.html', context)

    except ValueError as e:
        # Handle errors gracefully if stock data is invalid
        messages.error(request, f"Invalid or delisted stock symbol: {selected_stock}. Please enter a valid stock symbol.")
        return redirect('stockPred')

