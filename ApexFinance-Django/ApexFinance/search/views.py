from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from django.http import JsonResponse
from django.views import View
import yfinance as yf

# Create your views here.
def search(request):
        query = request.GET.get('q', default="AAPL")  # Get search query from the form, default to AAPL if none

        if query:
            # Fetch stock data using yfinance
            quote = yf.Ticker(query)
            stock_info = quote.info
            return render(request, 'search/search.html', {'stock_info': stock_info, 'query': query})
        else:
            return render(request, 'search/search.html', {'error': 'No stock symbol provided.'})

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
        # Determine the interval based on the selected period
        interval = self.get_interval(period)
        
        # pull the quote
        quote = yf.Ticker(symbol)
        
        # use the quote to pull the historical data from Yahoo Finance
        hist = quote.history(period=period, interval=interval)
        
        # convert the historical data to JSON
        data = hist.to_json()
        
        # return the JSON in the HTTP response
        return JsonResponse(data, safe=False)  # Use safe=False for non-dict objects
    
    def get_interval(self, period):
            """Determine the interval based on the selected period."""
            if period == '1d':
                return '1m'  # 1 min intervals for 1 day
            elif period == '5d':
                return '30m'  # 20 min intervals for 5 days
            elif period in ['1mo', '3mo']:
                return '1d'  # Daily intervals for 1 month and 3 months
            elif period == '1y':
                return '5d'  # 5 day intervals for 1 year
            elif period == 'ytd':
                return '5d' # 5 day intervals for ytd
            elif period == '2y':
                return '5d'  # 5 day intervals for 2 year
            elif period in ['5y', 'max']:
                return '1mo' # Monthly intervals for 5 year and beyond
            else:
                return '1mo'  # Default for any unknown period