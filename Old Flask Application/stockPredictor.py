# Ensure you have the required packages
# pip install streamlit yfinance prophet plotly

import streamlit as st
from datetime import date

import yfinance as yf
from prophet import Prophet  # Updated import for the latest Prophet version
from prophet.plot import plot_plotly
from plotly import graph_objs as go

# Set the start and today dates
START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

st.title('Stock Forecast App')

# List of stock tickers
stocks = ('GOOG', 'AAPL', 'MSFT', 'GME')
selected_stock = st.selectbox('Select dataset for prediction', stocks)

# Slider for selecting the number of years for prediction
n_years = st.slider('Years of prediction:', 1, 4)
period = n_years * 365

# Cache the data loading function
@st.cache_data  # Updated from @st.cache to @st.cache_data
def load_data(ticker):
    data = yf.download(ticker, START, TODAY)
    data.reset_index(inplace=True)
    return data

# Loading state text
data_load_state = st.text('Loading data...')
data = load_data(selected_stock)
data_load_state.text('Loading data... done!')

# Display the raw data
st.subheader('Raw data')
st.write(data.tail())

# Function to plot raw data
def plot_raw_data(data):  # Added 'data' parameter
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name="stock_open"))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="stock_close"))
    fig.layout.update(title_text='Time Series data with Rangeslider', xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)

# Call the plotting function
plot_raw_data(data)


print(data)
# Prepare the data for forecasting
df_train = data[['Date', 'Close']]
df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

# Initialize and fit the Prophet model
m = Prophet()
m.fit(df_train)

# Create future dataframe for predictions
future = m.make_future_dataframe(periods=period)
forecast = m.predict(future)

# Show and plot the forecast data
st.subheader('Forecast data')
st.write(forecast.tail())

st.write(f'Forecast plot for {n_years} years')
fig1 = plot_plotly(m, forecast)
st.plotly_chart(fig1)

st.write("Forecast components")
fig2 = m.plot_components(forecast)
st.write(fig2)