import requests
import time
import hashlib
import hmac
import matplotlib.pyplot as plt
import numpy as np
import math
from pybit import usdt_perpetual
#from binance.client import Client
#from binance.enums import *

# Initialize your API Keys and Secrets for Binance and Bybit
BINANCE_API_KEY = 'FAwoao710g15n9CYv3FXiaclCpGN59V8XK8ipHIyi6wykO6JrSmPa0optsmH02W3'
BINANCE_API_SECRET = 'AiP11eVHbtaL73JdlGcNIsO4yaSHMSl8yhCrbRxg9Bb6qPaTPGl8og5dQMn6KMvo'
BYBIT_API_KEY = '7JeEcSvWEW7c2VGBdI'
BYBIT_API_SECRET = 'zobIPQ0YIOzkPwiDdM8A8V0P1ZmrCdAQaHZJ'

# Function to get current price from Binance, symbol is a string

def get_binance_price(symbol):
    url = f'https://api.binance.com/api/v3/ticker/bookTicker?symbol={symbol}'

    response = requests.get(url)
    response.raise_for_status()  # Check if the request was successful
    data = response.json()

    # Extracting the bid and ask prices
    bid_price = float(data['bidPrice'])
    ask_price = float(data['askPrice'])

    # Calculating the spread
    spread = ask_price - bid_price

    return bid_price, ask_price, spread


# Function to get current price from Bybit, SYMBUSDT is a string

def get_bybit_price(symbol):
    r = requests.get(f'https://api.bybit.com/v2/public/tickers?symbol={symbol}')
    r.raise_for_status()  # Raise an HTTPError for bad responses
    data = r.json()

    # Accessing the 'bid_price' and 'ask_price' keys from the first dictionary in the list
    bid_price = float(data['result'][0]['bid_price'])
    ask_price = float(data['result'][0]['ask_price'])

    # Calculating the spread
    spread = ask_price - bid_price

    return bid_price, ask_price, spread

def is_ao(symbol, seuil):  # Boolean function which returns true if there exists an arbitrage opportunity.

    bi_bid_price, bi_ask_price, bi_spread = get_binance_price(symbol)
    by_bid_price, by_ask_price, by_spread = get_bybit_price(symbol)

    if (by_ask_price - bi_bid_price) / bi_bid_price > seuil:
        return True
    # elif  (bi_ask_price - by_bid_price) / by_bid_price > seuil: #cannot short on binance
    # return True
    else:
        return False


def binance_order(side, quantity, trading_pair):  # side : either "SIDE_SELL" or "SIDE_BUY", attention à la quantité minimum,

    client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

    # Set the trading pair, order type, and quantity for your conversion
    trading_pair = 'SOLUSDT'
    order_type = None #ORDER_TYPE_MARKET
    quantity = 0.28  # The amount of ETH you want to sell for BTC

    # Place the order
    order = client.create_order(
        symbol=trading_pair,
        side=SIDE_SELL,
        type=order_type,
        quantity=quantity
    )

    # Output the response (order result)
    return print(order)


# Function to place an order on Bybit in pybit version 2.4.1
session = usdt_perpetual.HTTP(
    endpoint='https://api.bybit.com',
    api_key='BYBIT_API_KEY',
    api_secret='BYBIT_API_SECRET'
)

# Get orderbook.
print(session.orderbook(symbol='SOLUSDT'))

# Create five long orders.
orders = {
    "symbol": "SOLUSDT",
    "order_type": "Limit",
    "side": "Buy",
    "qty": 0.1,
    "price": 25,
    "time_in_force": "GoodTillCancel"
}

# Submit the orders in bulk.
print(session.place_active_order(**orders))

print(session.cancel_all_active_orders(symbol="SOLUSDT"))


def bybit_order(side, quantity, symbol):
    timestamp = str(int(time.time() * 1000))
    params = {
        'api_key': BYBIT_API_KEY,
        'side': side,
        'symbol': symbol,
        'order_type': 'Market',
        'qty': quantity,
        'time_in_force': 'GTC',
        'timestamp': timestamp,
    }

    # Generate the signature
    ordered_params = '&'.join([f"{key}={params[key]}" for key in sorted(params)])
    signature = hmac.new(BYBIT_API_SECRET.encode(), ordered_params.encode(), hashlib.sha256).hexdigest()

    params['sign'] = signature

    headers = {
        'api-key': BYBIT_API_KEY
    }

    r = requests.post('https://api.bybit.com/v2/private/order/create', headers=headers, params=params)
    return r.json()
