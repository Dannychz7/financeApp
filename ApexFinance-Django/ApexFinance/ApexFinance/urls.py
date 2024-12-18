"""
URL configuration for ApexFinance project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from home import views
from dashboard import views
from settings import views
from search import views
from transactionHistory import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/home', permanent=False)), # Adds default page so the '/' redirects to the home page 
    path('', include("home.urls")),
    path('', include("dashboard.urls")),
    path('', include("settings.urls")),
    path('', include("search.urls")),
    path('', include("transactionHistory.urls")),
    path('users/', include('django.contrib.auth.urls')),
    path('users/', include('users.urls')),
]
