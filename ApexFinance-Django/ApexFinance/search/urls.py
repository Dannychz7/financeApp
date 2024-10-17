from django.urls import path
from .views import StockQuoteView, StockHistoryView, search

from . import views

urlpatterns = [
    path('search', views.search, name='search'),
    path('quote/', StockQuoteView.as_view(), name='stock_quote'),
    path('history/', StockHistoryView.as_view(), name='stock_history'),
]