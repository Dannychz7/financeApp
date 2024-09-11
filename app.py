from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('search.html')

@app.route('/stock-data', methods=['GET'])
def get_stock_data():
    stock_symbol = request.args.get('symbol', 'AAPL')
    ticker = yf.Ticker(stock_symbol)
    data = ticker.history(period="1d", interval="1m")

    data_json = {
        'time': list(data.index.strftime('%Y-%m-%d %H:%M:%S')),
        'close': list(data['Close'])
    }
    return jsonify(data_json)

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Use port 5001 instead

