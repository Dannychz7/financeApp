from flask import Flask, render_template,request
import yfinance as yf
import datetime

app = Flask(__name__)

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/FinanceAppUI')
def dashboard():
    return render_template('FinanceAppUI.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    stock_symbol = request.args.get('stockSymbol', 'AAPL')  # Default to AAPL if no symbol provided
    stock = yf.Ticker(stock_symbol)
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    data = stock.history(start=today, end=today)
    
    # Convert data to a dictionary for easy use in the template
    data_dict = data.reset_index().to_dict(orient='records')
    
    return render_template('search.html', data=data_dict, symbol=stock_symbol)

@app.route('/settings')
def settings():
    return render_template('settings.html')


if __name__ == '__main__':
    app.run(debug=True)
