from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime

# Create your views here.
def home(request):
    return render(request, 'home/welcome.html', {'today': datetime.today()})

def FAQ(request):
    return render(request, 'home/FAQ.html', {})

def aboutUs(request):
    return render(request, 'home/aboutUs.html', {})