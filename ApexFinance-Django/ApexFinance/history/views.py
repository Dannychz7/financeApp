from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.models import StockTransaction

@login_required
def transaction_history(request):
    # Fetch transactions related to the logged-in user's profile
    transactions = StockTransaction.objects.filter(profile=request.user.profile).order_by('-transaction_date')
    
    # Prepare the context
    context = {
        'transactions': transactions,
    }
    
    # Render the template with the context
    return render(request, 'history/history.html', context)