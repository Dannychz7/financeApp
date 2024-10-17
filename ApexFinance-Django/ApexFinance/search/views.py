from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from django.http import JsonResponse
from django.views import View
import yfinance as yf

# Create your views here.
def search(request):
    return render(request, 'search/search.html', {})

class StockQuoteView(View):
    def get(self, request):
        # get a stock ticker symbol from the query string, default to AAPL
        symbol = request.GET.get('symbol', default="AAPL")
        
        # pull the stock quote
        quote = yf.Ticker(symbol)
        
        # return the object via the HTTP response
        return JsonResponse(quote.info)

class StockHistoryView(View):
    def get(self, request):
        # get the query string parameters
        symbol = request.GET.get('symbol', default="AAPL")
        period = request.GET.get('period', default="1y")
        interval = request.GET.get('interval', default="1mo")
        
        # pull the quote
        quote = yf.Ticker(symbol)
        
        # use the quote to pull the historical data from Yahoo Finance
        hist = quote.history(period=period, interval=interval)
        
        # convert the historical data to JSON
        data = hist.to_json()
        
        # return the JSON in the HTTP response
        return JsonResponse(data, safe=False)  # Use safe=False for non-dict objects