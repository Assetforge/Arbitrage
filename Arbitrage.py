import requests
import time
import hashlib
import hmac
import matplotlib.pyplot as plt
import numpy as np
import math
from binance.client import Client
from binance.enums import *
from pybit.unified_trading import HTTP

# Initialize your API Keys and Secrets for Binance and Bybit
BINANCE_API_KEY = 'FAwoao710g15n9CYv3FXiaclCpGN59V8XK8ipHIyi6wykO6JrSmPa0optsmH02W3'
BINANCE_API_SECRET = 'AiP11eVHbtaL73JdlGcNIsO4yaSHMSl8yhCrbRxg9Bb6qPaTPGl8og5dQMn6KMvo'
BYBIT_API_KEY = '7JeEcSvWEW7c2VGBdI'
BYBIT_API_SECRET = 'zobIPQ0YIOzkPwiDdM8A8V0P1ZmrCdAQaHZJ'

global binance_position_open
global bybit_position_open
binance_position_open = False
bybit_position_open = False

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


def is_ao(symbol, seuil):  # Boolean function which returns true if there exists an arbitrage opportunity. Seuil between 0 and 1

    bi_bid_price, bi_ask_price, bi_spread = get_binance_price(symbol)
    by_bid_price, by_ask_price, by_spread = get_bybit_price(symbol)

    if (by_ask_price - bi_bid_price) / bi_bid_price > seuil:
        return True
    #elif  (bi_ask_price - by_bid_price) / by_bid_price > seuil: #cannot short on binance
        #return True
    else:
        return False

def is_to_close(symbol, seuil):  # Boolean function which returns true if the price difference is negligeable to the Seuil between 0 and 1

    bi_bid_price, bi_ask_price, bi_spread = get_binance_price(symbol)
    by_bid_price, by_ask_price, by_spread = get_bybit_price(symbol)

    if (by_ask_price - bi_bid_price) / bi_bid_price < seuil:
        return True
    else:
        return False


def binance_order(Side, quantity, trading_pair) : # Side : either SIDE_SELL or SIDE_BUY, attention à la quantité minimum. EX : binance_order(SIDE_BUY, 0.03, "BNBUSDT")



    if Side == SIDE_BUY:
        binance_position_open = True
        print(f"Opening Binance position: BUY {quantity} {trading_pair}")
    elif Side == SIDE_SELL and binance_position_open:
        binance_position_open = False
        print(f"Closing Binance position: SELL {quantity} {trading_pair}")

    client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
    order_type = ORDER_TYPE_MARKET

    # Place the order
    order = client.create_order(
        symbol=trading_pair,
        side=Side,
        type=order_type,
        quantity=quantity
    )
    return print(order)


#Function to place an order on Bybit

def bybit_order(Side, quantity, trading_pair) : # Side : "Buy" or "Sell", quantity in bracket  trading_pair "SOLUSDT", bybit_order("Buy", "0.1", "SOLUSDT")



    if side == "Sell":
        bybit_position_open = True
        print(f"Opening Bybit position: SELL {quantity} {trading_pair}")
    elif side == "Buy" and bybit_position_open:
        bybit_position_open = False
        print(f"Closing Bybit position: BUY {quantity} {trading_pair}")

    session = HTTP(
        testnet=False,
        api_key = BYBIT_API_KEY,
        api_secret = BYBIT_API_SECRET,
    )

    order = session.place_order(
        category="linear",
        symbol=trading_pair,
        side=Side,
        orderType="Market",
        qty=quantity,
        timeInForce="FillOrKill",
        isLeverage=0,
        )
    return print(order)

# Idée : vérification si les deux positions ont bien été ouvertes pour continuer.
#quand et comment fermer la position ?


def main(trading_pair):

    while True:  # Infinite loop to keep the script running
        try:
            if is_ao(trading_pair, 0.001):
                print("Arbitrage opportunity detected")
                binance_order(SIDE_BUY, 0.2, trading_pair)
                bybit_order("Sell", "0.2", trading_pair) #add str(quantity) as a parameter in the function

            if is_to_close(trading_pair, 0.001) and is_to_close(trading_pair, 0.001) and binance_position_open and bybit_position_open:
                print("position closed")
                binance_order(SIDE_SELL, 0.2, trading_pair)
                bybit_order("Buy", "0.2", trading_pair)

            if not is_ao(trading_pair, 0.005):
                print("No arbitrage opportunity at the moment.")

        except Exception as e:
            print(f"An error occurred: {e}")

        time.sleep(1)  # Wait for 1 second before checking again




## To add and modify

#Global variables referenced before assignement
#Find a way to close the position because of the fees the buy quantity is too high to close
# -> Define criteria and conditions when and how to exit the trade -> Take a look at security issues concerning API Keys
# -> Define a size limit on transaction -> Number of active position equal to one at first -> Arbitrage of one asset at first
#
# IMPROVE SPEED

#RISK MANAGEM


