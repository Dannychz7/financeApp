from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views

urlpatterns = [
    path('settings', views.settings, name= "settings"),
    path('logout/', views.logoutPage, name='logoutPage'),

]