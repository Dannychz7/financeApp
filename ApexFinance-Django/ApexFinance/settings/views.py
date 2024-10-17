from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
import os

# Create your views here.
def settings(request):
    print("Current directory:", os.getcwd())  # Debugging line
    return render(request, 'settings/settings.html', {})