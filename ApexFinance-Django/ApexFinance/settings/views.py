from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from datetime import datetime
from django.contrib.auth import logout
from django.shortcuts import redirect, render
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from users.models import Profile, UserStock, StockTransaction  # Make sure to import Profile
from decimal import Decimal
import yfinance as yf
import os

# User authorization
from django.contrib.auth.decorators import login_required

# Require users to be logged into an account to see their settings
@login_required(login_url='/users/login_user')
def settings(request):
    # Get the current user's profile
    profile = request.user.profile

    # Get all the stocks the user owns
    user_stocks = UserStock.objects.filter(profile=profile)

    # Get available cash
    available_cash = profile.available_cash

    # Calculate the total stock value
    total_stock_value = Decimal(0)
    for stock in user_stocks:
        stock_data = yf.Ticker(stock.company_name)
        data = stock_data.info

        # Get the current stock price
        if data.get('quoteType') in ['MUTUALFUND', 'ETF']:
            current_price = Decimal(data.get('previousClose', 0))
        else:
            current_price = Decimal(data.get('currentPrice', data.get('ask', data.get('regularMarketPrice', 0))))

        # Add to the total stock value
        stock_value = stock.stock_quantity * current_price
        total_stock_value += stock_value

    # Update the total portfolio value
    total_portfolio_value = available_cash + total_stock_value

    # Prepare context data for the template
    context = {
        'total_portfolio_value': float(total_portfolio_value),
        'available_cash': float(available_cash),
        'user': request.user.username,  # Pass the username
        'email': request.user.email,
    }

    # Render the template with the context data
    return render(request, 'settings/settings.html', context)


def logoutPage(request):
    if request.method == 'POST':
        logout(request)  # Logs out the user
        return redirect('logoutPage')  # Redirect to the homepage or wherever you want
    return render(request, 'settings/logoutPage.html')  # Render the page if it's a GET request

@login_required(login_url='/users/login_user')
def changePswd(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Keep the user logged in after password change
            messages.success(request, "Your password was updated successfully. You can now use your new password.")
            return redirect('change_pswd')  # Redirect to change password page after success
        else:
            # Check for specific form errors and customize the error messages
            for field, errors in form.errors.items():
                for error in errors: # This line will print all errors in the form
                    messages.error(request, f"Error: {error}")
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'settings/changePswd.html', {'form': form})
