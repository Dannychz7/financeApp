from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
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