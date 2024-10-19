from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from users.models import UserStock  # Import the UserStock model

# User authorization
from django.contrib.auth.decorators import login_required

# Require users to be logged into an account to see their dashboard
@login_required(login_url='/users/login_user')
def dashboard(request):
    profile = request.user.profile  # Access the profile of the logged-in user
    # Get all stocks for the logged-in user
    user_stocks = UserStock.objects.filter(profile=request.user.profile)
    
    # Get the cash available for the user (assuming this is part of the Profile model)
    available_cash = profile.available_cash  # Get available cash

    # Render the dashboard template with the user's stocks and available cash
    return render(request, 'dashboard/dashboard.html', {
        'user_stocks': user_stocks,
        'available_cash': available_cash,
    })