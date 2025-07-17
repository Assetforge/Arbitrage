import requests
import time
import aiohttp
import threading
import asyncio
import matplotlib.pyplot as plt
from binance.client import Client
from binance.enums import *
from pybit.unified_trading import HTTP
from binance.exceptions import BinanceAPIException, BinanceOrderException
from decimal import Decimal, ROUND_DOWN
# import numpy as np
# import math


je suis jean michelle
## Keys and global variables
# Initialize your API Keys and Secrets for Binance and Bybit
BINANCE_API_KEY = ''
BINANCE_API_SECRET = ''
BYBIT_API_KEY = ''
BYBIT_API_SECRET = ''

#Telegram keys
bot_token = ''
chat_id = ""

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
bybit_session = HTTP(testnet=False, api_key=BYBIT_API_KEY, api_secret=BYBIT_API_SECRET)
binance_session = requests.Session()

#global variables
fee_by, fee_bi = 0.055/100, 0.1/100
positions_open = False

## Functions


def get_by_fr(symbol):
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

def bi_order(trading_pair, side, quantity ):
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


def telegram_bot_sendtext(bot_message):
    send_text1 = 'https://api.telegram.org/bot' + bot_token + \
                 '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + bot_message
    response1 = requests.get(send_text1)
    return (response1.json())


def check_for_stop_command():
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    response = requests.get(url)
    messages = response.json().get('result', [])
    if messages[-1].get('message', {}).get('text', '') == 'Stop' and messages[-1].get('message', {}).get('chat', {}).get('username', '') == 'matheolentz':
        return True
    return False

## Main function

def main(trading_pair, quantity, seuil_a, seuil_c):
    global positions_open
    symbol = trading_pair.replace("USDT", "")

    while True:
        try:
            result_dict = fetch_prices_parallel(trading_pair)
            bi_bp, bi_ap = result_dict["bi"]
            by_bp, by_ap = result_dict["by"]
            is_ao = ((1-fee_by)*by_bp - (1+fee_bi)*bi_ap )/bi_ap > seuil_a/100
            is_to_close = ((1+fee_by)*by_ap - (1-fee_bi)*bi_bp)/bi_bp < seuil_c/100

            if is_ao and not positions_open:
                place_orders_concurrently(trading_pair, SIDE_BUY, "Sell", quantity)
                print(f"Arbitrage opportunity detected : Sell Bybit {by_bp}, Buy Binance {bi_ap} \n")
                buy, sell = bi_ap, by_bp 
                telegram_bot_sendtext(f"Arbitrage opportunity detected : Sell Bybit {by_bp}, Buy Binance {bi_ap}")
                positions_open = True

            elif is_to_close and positions_open:
                place_orders_concurrently(trading_pair, SIDE_SELL, "Buy", quantity)
                telegram_bot_sendtext(f"Positions closed : Buy Bybit {by_ap}, Sell Binance {bi_bp}")
                print(f"Positions closed : Buy Bybit {by_ap}, Sell Binance {bi_bp}\n")
                positions_open = False

            # if positions_open :
            #     print("Waiting to close positions \n")
            #
            #elif not is_ao and not positions_open:
                #print("No arbitrage opportunity at the moment.\n")

            # if check_for_stop_command() :
            #     telegram_bot_sendtext("Stop command received. Exiting.")
            #     print("Stop command received. Exiting. \n")
            #     break
            #  time.sleep(0.5)

        except Exception as e:
            telegram_bot_sendtext(f"An error occurred: {e}")
            print(f"An error occurred: {e}")
            if str(e) == "APIError(code=-1013): Filter failure: NOTIONAL":
                break
            elif str(e)=="('Connection aborted.', OSError(50, 'Network is down'))":
                break
            elif str(e)=="('Connection aborted.', TimeoutError(60, 'Operation timed out'))":
                break
            elif str(e)=="bi" or str(e)=="by":
                break
