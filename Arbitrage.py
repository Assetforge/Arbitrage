import requests
import time
import matplotlib.pyplot as plt
from binance.client import Client
from binance.enums import *
from pybit.unified_trading import HTTP
from binance.exceptions import BinanceAPIException, BinanceOrderException
from decimal import Decimal, ROUND_DOWN
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


def get_bi_price(symbol):
    url = f'https://api.binance.com/api/v3/ticker/bookTicker?symbol={symbol}'
    data = binance_session.get(url).json()
    return float(data['bidPrice']), float(data['askPrice'])


def get_by_price(symbol):
    url = f'https://api.bybit.com/v2/public/tickers?symbol={symbol}'
    data = requests.get(url).json()['result'][0]
    return float(data['bid_price']), float(data['ask_price'])


def is_ao(symbol, seuil):  # Boolean function which returns true if there exists an arbitrage opportunity. Seuil between 0 and 1
    bi_bid_price, bi_ask_price = get_bi_price(symbol)
    by_bid_price, by_ask_price = get_by_price(symbol)
    return (by_ask_price - bi_bid_price) / bi_bid_price > seuil


def is_to_close(symbol, seuil):  # Boolean function which returns true if the price difference is negligeable to the Seuil between 0 and 1
    bi_bid_price, bi_ask_price = get_bi_price(symbol)
    by_bid_price, by_ask_price = get_by_price(symbol)
    return (by_ask_price - bi_bid_price) / bi_bid_price < seuil


def bi_order(side, quantity, trading_pair):
    print(f"{'Opening' if side == SIDE_BUY else 'Closing'} Binance position: {side} {quantity} {trading_pair}\n")
    return client.create_order(symbol=trading_pair, side=side, type=ORDER_TYPE_MARKET, quantity=quantity)


def by_order(side, quantity, trading_pair):
    print(f"{'Opening' if side == 'Sell' else 'Closing'} Bybit position: {side} {quantity} {trading_pair}\n")
    return bybit_session.place_order(category="linear", symbol=trading_pair, side=side, orderType="Market", qty=quantity, timeInForce="FillOrKill", isLeverage=0)


def get_asset_balance(asset):#for BINANCE !
    return client.get_asset_balance(asset=asset)


def main(trading_pair, quantity, seuil_a, seuil_c):

    positions_open = False
    symbol = trading_pair.replace("USDT", "")

    while True:
        try:
            if is_ao(trading_pair, seuil_a) and not positions_open :
                print("Arbitrage opportunity detected. \n")
                bi_order(SIDE_BUY, quantity, trading_pair)
                by_order("Sell", str(quantity), trading_pair)
                positions_open = True

            if is_to_close(trading_pair, seuil_c) and positions_open: # and bybit_position_open
                asset_balance = Decimal(get_asset_balance(symbol)['free'])
                asset_balance_adj = asset_balance.quantize(Decimal('0.01'), rounding=ROUND_DOWN)# A adapter à la crypto arbitrée

                bi_order(SIDE_SELL, asset_balance_adj, trading_pair)
                by_order("Buy", str(asset_balance_adj), trading_pair)
                positions_open = False
                print("position closed. \n")

            if positions_open :
                print("Waiting to close positions \n")

            if not is_ao(trading_pair, seuil_a) and not positions_open:
                print("No arbitrage opportunity at the moment.\n")


        except Exception as e:
            print(f"An error occurred: {e}")
            break

        time.sleep(2)  # Wait for 1 second before checking again


#main("TRBUSDT", 0.25, 0.007, 0.0001)

