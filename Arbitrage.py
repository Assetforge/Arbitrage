import requests
import time
import hashlib
import hmac
import matplotlib.pyplot as plt
import numpy as np
import math


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

print(get_binance_price("SOLUSDT"))


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

print(get_bybit_price("SOLUSDT"))


def is_ao(symbol, seuil): #Boolean function which returns true if there exists an arbitrage opportunity.

    bi_bid_price, bi_ask_price, bi_spread = get_binance_price(symbol)
    by_bid_price, by_ask_price, by_spread = get_bybit_price(symbol)

    if (by_ask_price-bi_bid_price)/bi_bid_price > seuil :
        return True
    elif (bi_ask_price-by_bid_price)/by_bid_price > seuil :
        return True
    else :
        return False

print(is_ao('TRBUSDT', 0.05))

# Function to place an order on Binance
def binance_order(side, quantity):
    timestamp = int(time.time() * 1000)
    params = {
        'symbol': 'SOLUSDT',
        'side': side,
        'type': 'MARKET',
        'quantity': quantity,
        'timestamp': timestamp,
    }

    query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
    signature = hmac.new(BINANCE_API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()

    params['signature'] = signature

    headers = {
        'X-MBX-APIKEY': BINANCE_API_KEY
    }

    r = requests.post('https://api.binance.com/api/v3/order', headers=headers, params=params)
    return r.json()


# Function to place an order on Bybit
def bybit_order(side, quantity, symbol):
    timestamp = str(int(time.time() * 1000))
    params = {
        'api_key': BYBIT_API_KEY,
        'side': side,
        'symbol': symbol,
        'order_type': 'Market',
        'qty': str(quantity),
        'time_in_force': 'GTC',
        'timestamp': timestamp,
    }

    params_str = '&'.join([f"{key}={params[key]}" for key in sorted(params)])
    signature = hashlib.sha256((params_str + BYBIT_API_SECRET).encode('utf-8')).hexdigest()

    params['sign'] = signature

    headers = {
        'api-key': BYBIT_API_KEY
    }

    r = requests.post('https://api.bybit.com/v2/private/order/create', headers=headers, params=params)
    return r.json()





