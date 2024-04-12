import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import csv
import requests
from flask import Flask, render_template, request
import io

app = Flask(__name__)
app.config["DEBUG"] = True

# Function to import stock symbols from CSV
def import_symbols():
    with open('stocks.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)
        symbols = [row[0] for row in reader]
    return symbols

# Stock data function to query API
def get_stock_data(symbol, function, start_date, end_date, api_key, interval=None):
    if function.startswith('TIME_SERIES_INTRADAY'):
        url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&interval={interval}&apikey={api_key}&outputsize=full"
    else:
        url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={api_key}&outputsize=full"
    
    response = requests.get(url)
    data = response.json()
    
    if 'Time Series (Daily)' in data:
        time_series_data = data['Time Series (Daily)']
    elif 'Weekly Time Series' in data:
        time_series_data = data['Weekly Time Series']
    elif 'Monthly Time Series' in data:
        time_series_data = data['Monthly Time Series']
    else:
        print(f"Error: {function} data not found in API response.")
        return None
    
    filtered_data = {date: values for date, values in time_series_data.items()
                     if start_date <= date <= end_date}
    
    if not filtered_data:
        print(f"No data found for {symbol} within the given date range. Please try a different date range.")
        return None
    
    return filtered_data

# Graph
def generate_graph(data, chart_type):
    dates = list(data.keys())
    prices = [float(data[date]['4. close']) for date in dates]
    
    plt.figure(figsize=(10, 6))
    if chart_type == 'line':
        plt.plot(dates, prices, label='Close Price')
    elif chart_type == 'bar':
        plt.bar(dates, prices, color='skyblue', label='Close Price')
    elif chart_type == 'scatter':
        plt.scatter(dates, prices, color='red', label='Close Price')
    
    plt.title('Stock Prices Over Time')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    
    plt.savefig('static/stock_plot.svg')

@app.route('/', methods=['GET', 'POST'])
def main():
    symbols = import_symbols()

    if request.method == 'POST':
        symbol = request.form['symbol']
        function = request.form['function']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        chart_type = request.form['chart_type']

        api_key = "VHI1NLV7FLZATH71"
        interval = None
        if function == 'TIME_SERIES_INTRADAY':
            interval = request.form['interval']

        stock_data = get_stock_data(symbol, function, start_date, end_date, api_key, interval)
        if stock_data is None:
            return "No data found for the selected symbol and date range."
        
        generate_graph(stock_data, chart_type)
        return render_template('result.html', symbol=symbol, chart_type=chart_type)

    return render_template('index.html', symbols=symbols)

if __name__ == "__main__":
    app.run(host="0.0.0.0")