from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime

# User authorization
from django.contrib.auth.decorators import login_required

# Require users to be logged into an account to see their dashboard
@login_required(login_url='/users/login_user')
def dashboard(request):
    return render(request, 'dashboard/dashboard.html',{})