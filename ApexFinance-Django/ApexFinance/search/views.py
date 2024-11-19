from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from django.http import JsonResponse
from django.views import View
import yfinance as yf
# User authorization
from django.contrib.auth.decorators import login_required

# Require users to be logged into an account to search
@login_required(login_url='/users/login_user')
# Create your views here.
def search(request):
        query = request.GET.get('q', default="AAPL")  # Get search query from the form, default to AAPL if none
        
        if query:
            # Fetch stock data using yfinance
            quote = yf.Ticker(query)
            stock_info = quote.info
            
            # # Store stock_info and query in session
            # request.session['stock_info'] = stock_info
            # request.session['query'] = query
            
            return render(request, 'search/search.html', {'stock_info': stock_info, 'query': query})
        else:
            return render(request, 'search/search.html', {'error': 'No stock symbol provided.'})

class StockQuoteView(View):
    def get(self, request):
        # get a stock ticker symbol from the query string, default to AAPL
        symbol = request.GET.get('symbol', default="AAPL")
        # print("Here is the stock ", symbol)
        
        request.session['query'] = symbol
        
        #print(symbol)
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
                return '15m'  # 15 min intervals for 5 days
            elif period in ['1mo', '3mo']:
                return '60m'  # Daily intervals for 1 month and 3 months
            elif period == '1y':
                return '1d'  # 5 day intervals for 1 year
            elif period == 'ytd':
                return '1d' # 5 day intervals for ytd
            elif period == '2y':
                return '5d'  # 5 day intervals for 2 year
            elif period in ['5y', 'max']:
                return '1mo' # Monthly intervals for 5 year and beyond
            else:
                return '1mo'  # Default for any unknown period

class ExtraChartsView(View):
    def get(self, request):
        symbol = request.GET.get('symbol', default="AAPL")
        print(symbol)
        quote = yf.Ticker(symbol)
        sector = quote.info.get('sector', 'Technology')
        print(sector)

        # Fetch related stocks based on the sector
        related_stocks = self.get_related_stocks(sector)

        extra_charts_data = []
        for stock in related_stocks:
            related_quote = yf.Ticker(stock)
            stock_history = related_quote.history(period="1d", interval="1m")
            stock_history_json = stock_history.to_json()

            extra_charts_data.append({
                'symbol': stock,
                'shortName': related_quote.info.get('shortName', stock),
                'Price': related_quote.info.get('currentPrice', related_quote.info.get('previousClose', 0)),
                'Close': stock_history_json
            })
        
        # hist = quote.history(period=period, interval=interval) # Add an option for history? 
        # print(hist)

        # Return the data in JSON format for front-end consumption
        return JsonResponse(extra_charts_data, safe=False)

    def get_related_stocks(self, sector):
        print("Here I am in the get sector side: ", sector)
        """Fetch related stocks based on the sector."""
        if sector == 'Technology':
            return ['MSFT', 'GOOGL', 'AMZN', 'AAPL']
        elif sector == 'Healthcare':
            return ['JNJ', 'PFE', 'MRK', 'ABT', 'UNH']
        elif sector == 'Financial Services':
            return ['JPM', 'GS', 'C', 'WFC']
        elif sector == 'Consumer Staples':
            return ['KO', 'PG', 'PEP', 'CL']
        else:
            # Return popular ETFs if sector is not recognized
            return ['SPY', 'IVV', 'QQQ', 'VTI', 'VOO']