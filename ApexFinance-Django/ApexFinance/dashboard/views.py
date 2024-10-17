from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime

# Create your views here.
def dashboard(request):
    return render(request, 'dashboard/dashboard.html', {})