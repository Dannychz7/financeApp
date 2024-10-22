import yfinance as yf
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Profile, UserStock  # Make sure to import Profile
from .forms import UserRegistrationForm, BuyStockForm, SellStockForm
from decimal import Decimal
from django.utils import timezone

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Create the user but don't save it yet
            user.set_password(form.cleaned_data['password'])  # Set the password properly
            user.save()  # Now save the user
            Profile.objects.create(user=user)  # Create a profile for the user ***SET profile = Profile.objects.create(user=user) FOR DEBUGGING BELOW***
            
            # Create a default stock entry for NVDA ***USE FOR DEBUGGING***
            # UserStock.objects.create(
            #     profile=profile,
            #     company_name='NVDA',
            #     stock_quantity=10,  # Default quantity
            #     stock_price=250.00   # Default price (you can adjust this as needed)
            # )
            
            messages.success(request, "Registration successful! You can now log in.")  # Optional success message
            return redirect('login')  # Redirect to the login page
    else:
        form = UserRegistrationForm()
    return render(request, 'authentication/register.html', {'form': form})

def login_user(request):
    # Check if the form was submitted
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a dashboard after successful login
            return redirect('dashboard')
        else:
            # Show error message if login fails
            messages.error(request, "There was an error logging in. Try again.")
            return redirect('login')
    else:
        return render(request, 'authentication/login.html', {})
    
def buy_stock(request):
    if request.method == 'POST':
        form = BuyStockForm(request.POST)
        if form.is_valid():
            company_name = form.cleaned_data['company_name']
            stock_quantity = form.cleaned_data['stock_quantity']
            
            profile = request.user.profile  # Get the user's profile
            available_cash = profile.available_cash
            
            # Fetch real stock price using yfinance
            stock_data = yf.Ticker(company_name)
            data = stock_data.info # Get the stock information
            
            # Determine the price based on quote type
            if data.get('quoteType') in ['MUTUALFUND', 'ETF']:
                stock_price = Decimal(data.get('previousClose', 0))  # Use previous close for ETFs and mutual funds
            else:
                stock_price = Decimal(data.get('currentPrice', data.get('ask', data.get('regularMarketPrice', 0))))  # Use current price or ask price for stocks
                    
            total_cost = stock_quantity * stock_price
            
            if available_cash >= total_cost:
                # Update available cash
                profile.available_cash = profile.available_cash - total_cost
                profile.save()
                
                # Check if stock already exists for the user
                user_stock, created = UserStock.objects.get_or_create(
                    profile=profile,
                    company_name=company_name,
                    defaults={'stock_quantity': 0, 'stock_price': stock_price, 'stock_purchase_date': timezone.now()}
                )
                
                # Update stock quantity
                user_stock.stock_quantity += stock_quantity
                user_stock.stock_purchase_date = timezone.now()  # Update the purchase date to the current date
                user_stock.save()

                messages.success(request, f"Successfully bought {stock_quantity} shares of {company_name}.")
                return redirect('search')
            else:
                messages.error(request, "Not enough cash to buy this stock.")
                return redirect('search')
            
            # return redirect('dashboard')
    else:
        form = BuyStockForm()

    return render(request, 'stocks/buy_stock.html', {'form': form})

def sell_stock(request):
    if request.method == 'POST':
        form = SellStockForm(request.POST)
        if form.is_valid():
            company_name = form.cleaned_data['company_name']
            stock_quantity = form.cleaned_data['stock_quantity']
            
            profile = request.user.profile  # Get the user's profile
            user_stock = UserStock.objects.filter(profile=profile, company_name=company_name).first()

            if user_stock and user_stock.stock_quantity >= stock_quantity:
                # Fetch real stock price using yfinance
                stock_data = yf.Ticker(company_name)
                data = stock_data.info # Get the stock information
                
                # Determine the price based on quote type
                if data.get('quoteType') in ['MUTUALFUND', 'ETF']:
                    stock_price = Decimal(data.get('previousClose', 0))  # Use previous close for ETFs and mutual funds
                else:
                    stock_price = Decimal(data.get('currentPrice', data.get('ask', data.get('regularMarketPrice', 0))))  # Use current price or ask price for stocks
                
                # Update stock quantity
                user_stock.stock_quantity = user_stock.stock_quantity - stock_quantity
                
                if user_stock.stock_quantity == 0:
                    user_stock.delete()  # Remove the stock entry if quantity is 0
                else:
                    user_stock.save()
                
                # Update available cash
                profile.available_cash += stock_quantity * stock_price
                profile.save()

                messages.success(request, f"Successfully sold {stock_quantity} shares of {company_name}.")
                return redirect('search')
            else:
                messages.error(request, "You do not have enough shares to sell.")
                return redirect('search')
            
            # return redirect('dashboard')
    else:
        form = SellStockForm()
    
    return render(request, 'stocks/sell_stock.html', {'form': form})