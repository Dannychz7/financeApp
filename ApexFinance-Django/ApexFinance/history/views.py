import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from datetime import datetime
from users.models import UserStock, StockTransaction  # Import the UserStock model
from decimal import Decimal
from django.contrib.auth.decorators import login_required

@login_required(login_url='/users/login_user')
def history(request):
    # Get all stocks for the logged-in user
    user_stocks = UserStock.objects.filter(profile=request.user.profile)
    # Fetch transactions related to the logged-in user's profile
    user_transactions = StockTransaction.objects.filter(profile=request.user.profile).order_by('-transaction_date')

    # Prepare the context
    user_history = [
        {
            'name': transaction.company_name,
            'price': float(transaction.stock_price),  # Ensure stock_price is float for JSON serialization
            'quantity': transaction.stock_quantity,
            'type': transaction.transaction_type,
            'date': transaction.transaction_date.timestamp() * 1000
        }
        for transaction in user_transactions
    ]

    return render(request, 'dashboard/dashboard.html', {
        'user_transactions': user_transactions,
        'user_history': json.dumps(user_history) 
    })

@login_required(login_url='/users/login_user')
def TransactionHistory(request):
    # Get the current user's profile
    profile = request.user.profile

    # Get the transactions that are from this user:
    user_transactions = StockTransaction.objects.filter(profile=request.user.profile).order_by('-transaction_date')

    transactions_dict = {}

    for transaction in user_transactions:
        transactions_dict[transaction.company_name] = { # Store all of the user_transactions data into the dict
            'quantity': transaction.stock_quantity,
            'price': float(transaction.stock_price),
            'type': transaction.transaction_type,
            'date': transaction.transaction_date.timestamp() * 1000 
        }

    # Return the users transaction history
    return JsonResponse({
        'transaction_history': transactions_dict
    })