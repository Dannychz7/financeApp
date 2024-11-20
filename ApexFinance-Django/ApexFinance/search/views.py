from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from django.http import JsonResponse
from django.views import View
import yfinance as yf
import random
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
        # print(symbol)
        quote = yf.Ticker(symbol)
        sector = quote.info.get('sector', 'Technology')
        # print(sector)

        # Fetch related stocks based on the sector
        related_stocks = self.get_related_stocks(sector, symbol)

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
        
        # Return the data in JSON format for front-end consumption
        return JsonResponse(extra_charts_data, safe=False)

    def get_related_stocks(self, sector, symbol):
        
        # Top 75 most popular ETFs
        popular_etfs = [
            "SPY", "IVV", "VOO", "QQQ", "VTI", "IWM", "XLF", "XLY", "XLI", "XLE", "XLB", "XLV", "XLC",
            "VUG", "VTV", "VO", "VYM", "SCHD", "SPYG", "SPYV", "IWB", "IWD", "IWF", "VGT", "VNQ", "SCHF",
            "EFA", "EEM", "GDX", "GLD", "SLV", "LQD", "BND", "AGG", "HYG", "TIP", "TLT", "IBB", "KBE", 
            "ARKK", "ARKG", "SPLG", "DIA", "VWO", "IEMG", "HEDJ", "PFF", "JNK", "MUB", "VDE", "VDC", "VFH",
            "VHT", "VWO", "VXX", "BIL", "SCHX", "SCHB", "GDXJ", "SOXX", "XOP", "LIT", "XRT", "FTEC", "SPYG",
            "SPYV", "JEM", "IJH", "IJR", "VIG", "NOBL", "PHDG", "IWS", "IWP"
        ]
        
        popular_stocks = [
            "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "GOOG", "TSLA", "META", "BRK.B", "UNH", "JNJ", "XOM", "JPM", "V", 
            "PG", "MA", "LLY", "HD", "CVX", "MRK", "PEP", "KO", "PFE", "ABBV", "AVGO", "TMO", "COST", "CSCO", "MCD", 
            "ADBE", "WMT", "ACN", "NEE", "BAC", "BMY", "WFC", "DHR", "RTX", "UPS", "INTC", "CMCSA", "TXN", "LIN", "PM", 
            "UNP", "HON", "LOW", "CRM", "SCHW", "IBM", "MS", "AMGN", "AMD", "CAT", "ORCL", "GS", "BLK", "GE", "SPGI", 
            "CVS", "MDT", "ISRG", "PLD", "LMT", "INTU", "ADP", "T", "EL", "NFLX", "C", "SYK", "TGT", "VRTX", "DE", 
            "QCOM", "ZTS", "BKNG", "NOW", "CI", "CB", "TMUS", "CL", "DUK", "AXP", "SO", "MMM", "MO", "BDX", "ANTM", 
            "APD", "AMT", "ADI", "REGN", "EQIX", "PGR", "MMC", "ITW", "COP", "KHC", "EOG", "BSX", "SLB", "EW", "GM", 
            "HUM", "NOC", "LRCX", "SHW", "TRV", "HCA", "PRU", "FISV", "NKE", "FDX", "ROST", "AON", "PSA", "ICE", "STZ", 
            "MCO", "AEP", "MRNA", "KMB", "IDXX", "BK", "CME", "WM", "DG", "CSX", "F", "GD", "D", "MET", "ECL", "ILMN", 
            "ETN", "VLO", "ALL", "ROP", "TT", "EMR", "FCX", "ORLY", "CMG", "TWTR", "CTAS", "PH", "OXY", "SPG", "PSX", 
            "TFC", "ED", "ROP", "HLT", "RSG", "COF", "DLR", "HPQ", "WBA", "ALGN", "KR", "IQV", "PAYX", "EQR", "ZBH", 
            "MTD", "NEM", "TROW", "DTE", "AIG", "VRSK", "FTV", "EXC", "PCAR", "SYY", "TTWO", "AJG", "AFL", "DFS", 
            "CARR", "BXP", "SRE", "MSCI", "YUM", "EPAM", "CHTR", "FIS", "CLX", "PPG", "AZO", "HIG", "XYL", "HES", 
            "FAST", "AWK", "RE", "CINF", "MTB", "WAT", "OTIS", "GLW", "GWW", "KEYS", "PEAK", "VTR", "K", "GPC", "OKE", 
            "BLL", "LKQ", "PFG", "LEN", "NVR", "NDAQ", "DAL", "HBAN", "PPL", "STE", "AMP", "CNC", "CPB", "NTRS", 
            "RJF", "CBOE", "RHI", "BKR", "IP", "HOLX", "TER", "WDC", "FMC", "TXT", "AAP", "NLOK", "RCL", "LYV", "WRB", 
            "IVZ", "WAB", "AOS", "HPE", "DOV", "STT", "VAR", "CFG", "AAL", "MOS", "NOV", "SWN", "FANG", "VNO", "FOX", 
            "TPR", "HBI", "ALLE", "DXC", "LKQ", "AIG", "PNR", "ZION", "NI", "CE", "NRG", "FRT", "UAA", "BBWI", "WU", 
            "SEE", "GPS", "NWS", "CF", "COO", "APA", "DISCA", "DISH", "PVH", "DVA", "IRM", "DYN", "ROL", "LEG", 
            "HAS", "BWA", "J", "KIM", "JWN", "AAP", "WHR", "UHS", "LB", "UNM", "COTY", "NWL", "LVS", "ALK", "XRX", 
            "TAP", "HST", "WY", "IEX", "MKC", "PKI", "CHRW", "DRI", "ARE", "EXPD", "FE", "TSCO", "GILD", "PKG", 
            "WRK", "HRL", "OKE", "CPRT", "KMX", "TRMB", "ULTA", "CDNS", "VMC", "ANSS", "FLT", "RMD", "KEY", "GL", 
            "ZBRA", "TMO", "CTLT", "ATO", "XYL", "VFC", "AME", "NDSN", "BAX", "FOXA", "IFF", "CF", "LYB", "HRB", 
            "BIO", "EXPE", "PXD", "FFIV", "NTAP", "EXR", "NLSN", "CDW", "JBLU", "MLM", "CMA", "PVH", "ROL", "CNP", 
            "DRI", "SWKS", "TROW", "TPR", "IPGP", "DRE", "EXR", "ABMD", "ZBRA", "TRMB", "STLD", "EVRG", "BEN", 
            "SWK", "TRV", "WRK", "HUN", "PPL", "LB", "HBAN", "IRM", "FBHS", "CXO", "ZTS"
        ]

        # Fetch the symbol's quoteType using yfinance
        ticker = yf.Ticker(symbol)
        info = ticker.info
        quote_type = info.get('quoteType', None)
        
        # If the symbol is an ETF, return three random ETFs from the popular list
        if quote_type == 'ETF':
            return random.sample(popular_etfs, 3)
        else:
            return random.sample(popular_stocks, 3)