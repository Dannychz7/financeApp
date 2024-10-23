import json
import yfinance as yf
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from datetime import datetime
from users.models import UserStock  # Import the UserStock model
from decimal import Decimal

# User authorization
from django.contrib.auth.decorators import login_required

# Require users to be logged into an account to see their dashboard
@login_required(login_url='/users/login_user')
def dashboard(request):
    # Get all stocks for the logged-in user
    user_stocks = UserStock.objects.filter(profile=request.user.profile)

    # Prepare data for the chart (convert to list of dictionaries)
    stock_data = [
        {
            'name': stock.company_name,
            'price': float(stock.stock_price),  # Ensure stock_price is float for JSON serialization
            'quantity': stock.stock_quantity
        }
        for stock in user_stocks
    ]

    # Render the dashboard template with the user's stocks, available cash
    return render(request, 'dashboard/dashboard.html', {
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

    # Update the total portfolio value in the user's profile
    
    profile.total_stock_value = total_stock_value
    profile.total_value = available_cash + total_stock_value  # Total value = cash + stock value
    profile.save()  # Save the updated profile
    
    # Return both the available cash and total portfolio value
    return JsonResponse({
        'available_cash': float(available_cash),
        'total_value': float(profile.total_value),
        'total_stock_value': float(total_stock_value), #Grabbing this one
    })