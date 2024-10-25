from django.urls import path
from . import views

urlpatterns = [
    path('dashboard', views.dashboard, name= "dashboard"),
    path("live_update", views.live_update, name="live_update"),
    path('assetCalc', views.assetCalc, name='assetCalc'),
    path('fetch_etf_holdings', views.fetch_etf_holdings, name='fetch_etf_holdings'),
    
]