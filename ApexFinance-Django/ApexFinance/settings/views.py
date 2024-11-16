from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from django.contrib.auth import logout
from django.shortcuts import redirect, render
import os

# User authorization
from django.contrib.auth.decorators import login_required

# Require users to be logged into an account to see their settings
@login_required(login_url='/users/login_user')
def settings(request):
    # Get the currently logged-in user
    user = request.user
    
    # Pass the user object to the template
    return render(request, 'settings/settings.html', {
        'user': user,  # Pass user data to the template
    })

def logoutPage(request):
    if request.method == 'POST':
        logout(request)  # Logs out the user
        return redirect('logoutPage')  # Redirect to the homepage or wherever you want
    return render(request, 'settings/logoutPage.html')  # Render the page if it's a GET request
