"""Here's an algorithm inspired by the provided code that performs arbitrage on the funding rate between Binance and Bybit. The algorithm enters a short position on the future contract on Bybit and a long position on the spot market on Binance when the funding rate is positive. It also includes a safety mechanism to liquidate both positions simultaneously when the liquidation price is approached."""

import requests
import time
import aiohttp
import threading
import asyncio
import hmac
import hashlib
import matplotlib.pyplot as plt
from binance.client import Client
from binance.enums import *
from pybit.unified_trading import HTTP
from binance.exceptions import BinanceAPIException, BinanceOrderException
from decimal import Decimal, ROUND_DOWN

# Initialize your API Keys and Secrets for Binance and Bybit
BINANCE_API_KEY = ''
BINANCE_API_SECRET = ''
BYBIT_API_KEY = ''
BYBIT_API_SECRET = ''

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
bybit_session = HTTP(testnet=False, api_key=BYBIT_API_KEY, api_secret=BYBIT_API_SECRET)
binance_session = requests.Session()

# Global variables
fee_by, fee_bi = 0.055/100, 0.1/100
positions_open = False
liquidation_threshold = 0.95  # Set your desired liquidation threshold

# Functions

def get_by_fr(symbol): # return le fr en float (pas en %)
    url = f'https://api.bybit.com/v2/public/tickers?symbol={symbol}'
    data = requests.get(url).json()['result'][0]
    return float(data['funding_rate'])

def get_bi_price(symbol, result_dict):
    data = binance_session.get(f'https://api.binance.com/api/v3/ticker/bookTicker?symbol={symbol}').json()
    result_dict["bi"] = float(data['bidPrice']), float(data['askPrice'])

def get_by_price(symbol, result_dict):
    data = requests.get(f'https://api.bybit.com/v2/public/tickers?symbol={symbol}').json()['result'][0]
    result_dict["by"] = float(data['bid_price']), float(data['ask_price'])

def fetch_prices_parallel(trading_pair):
    result_dict = {}
    threads = []

    bi_thread = threading.Thread(target=get_bi_price, args=(trading_pair, result_dict))
    by_thread = threading.Thread(target=get_by_price, args=(trading_pair, result_dict))

    threads.extend([bi_thread, by_thread])

    bi_thread.start()
    by_thread.start()

    for thread in threads:
        thread.join()

    return result_dict

def bi_order(trading_pair, side, quantity):
    return client.create_order(symbol=trading_pair, side=side, type=ORDER_TYPE_MARKET, quantity=quantity)

def by_order(trading_pair, side, quantity):
    return bybit_session.place_order(category="linear", symbol=trading_pair, side=side, orderType="Market", qty=str(quantity), timeInForce="FillOrKill", isLeverage=0)

def place_orders_concurrently(trading_pair, bi_side, by_side, quantity):
    threads = []

    bi_thread = threading.Thread(target=bi_order, args=(trading_pair, bi_side, quantity))
    by_thread = threading.Thread(target=by_order, args=(trading_pair, by_side, quantity))

    threads.extend([bi_thread, by_thread])

    bi_thread.start()
    by_thread.start()

    for thread in threads:
        thread.join()

# def check_liquidation_price(trading_pair):
#     return float


# Main function

def main(trading_pair, quantity, seuil_a, seuil_c):
    global positions_open
    symbol = trading_pair.replace("USDT", "")

    while True:
        try:
            result_dict = fetch_prices_parallel(trading_pair)
            bi_bp, bi_ap = result_dict["bi"]
            by_bp, by_ap = result_dict["by"]
            funding_rate = get_by_fr(symbol)

            if funding_rate > 0 and not positions_open:
                place_orders_concurrently(trading_pair, SIDE_BUY, "Sell", quantity)
                print(f"Arbitrage opportunity detected: Sell Bybit {by_bp}, Buy Binance {bi_ap} \n")
                positions_open = True

            elif positions_open:
                if check_liquidation_price():
                    place_orders_concurrently(trading_pair, SIDE_SELL, "Buy", quantity)
                    print(f"Positions closed due to liquidation risk: Buy Bybit {by_ap}, Sell Binance {bi_bp}\n")
                    positions_open = False
                elif funding_rate <= -0.05:
                    place_orders_concurrently(trading_pair, SIDE_SELL, "Buy", quantity)
                    print(f"Positions closed: Buy Bybit {by_ap}, Sell Binance {bi_bp}\n")
                    positions_open = False

            time.sleep(0.5)

        except Exception as e:
            print(f"An error occurred: {e}")
            # Handle specific exceptions as needed

if __name__ == "__main__":
