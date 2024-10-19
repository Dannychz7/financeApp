from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
import os

# User authorization
from django.contrib.auth.decorators import login_required

# Require users to be logged into an account to see their settings
@login_required(login_url='/users/login_user')
def settings(request):
    print("Current directory:", os.getcwd())  # Debugging line
    return render(request, 'settings/settings.html', {})