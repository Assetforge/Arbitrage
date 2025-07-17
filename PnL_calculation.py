import requests
import time
import matplotlib.pyplot as plt
from binance.client import Client
from binance.enums import *
from pybit.unified_trading import HTTP
from binance.exceptions import BinanceAPIException, BinanceOrderException
from decimal import Decimal, ROUND_DOWN
from requests.auth import HTTPBasicAuth
# import numpy as np
# import math

# Initialize your API Keys and Secrets for Binance and Bybit
BINANCE_API_KEY = ''
BINANCE_API_SECRET = ''
BYBIT_API_KEY = ''
BYBIT_API_SECRET = ''

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
bybit_session = HTTP(testnet=False, api_key=BYBIT_API_KEY, api_secret=BYBIT_API_SECRET)
binance_session = requests.Session()

# Compute and plot PNL

def pnl_bybit(category="linear", limit=15):

    # Fetch the PnL data
    response = bybit_session.get_closed_pnl(
        category="linear",
        limit=limit,
    )
    # Parse the response
    pnl_data = response.get('result', {}).get('list', [])
    pnl_data.sort(key=lambda x: x['createdTime'])

    # Compute cumulative PnL
    pnl_values = [float(data['closedPnl']) for data in pnl_data]
    cumulative_pnl = [sum(pnl_values[:i+1]) for i in range(len(pnl_values))]
    return pnl_values, cumulative_pnl

def pnl_binance():
    # Make the API request to get the trade history
    response = requests.get(
        'https://api.binance.com/api/v3/myTrades',
        auth=HTTPBasicAuth(BINANCE_API_KEY, BINANCE_API_SECRET),
        SYMBOL="TRBUSDT"
    )
    trades = response.json()

    # Your cumulative PnL is now in the pnl variable
    return pnl

def plot_total_pnl():
    # Fetch PNL data from Binance and Bybit
    pnl_binance = fetch_binance_pnl()
    pnl_bybit = fetch_bybit_pnl()

    # Add them together to get the total PNL
    total_pnl = pnl_binance + pnl_bybit

    # Create a time series plot with a single data point for simplicity
    # In a real-world scenario, you'd have a series of PNL values over time
    plt.plot([datetime.datetime.now()], [total_pnl], 'ro-')
    plt.title('Total PNL from Binance and Bybit')
    plt.ylabel('Total PNL')
    plt.xlabel('Time')
    plt.legend(['Total PNL'])
    plt.show()
