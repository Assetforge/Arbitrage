import requests
import time
import aiohttp
import asyncio
import matplotlib.pyplot as plt
from binance.client import Client
from binance.enums import *
from pybit.unified_trading import HTTP
from binance.exceptions import BinanceAPIException, BinanceOrderException
from decimal import Decimal, ROUND_DOWN
# import numpy as np
# import math
## Keys and global variables
# Initialize your API Keys and Secrets for Binance and Bybit
BINANCE_API_KEY = 'FAwoao710g15n9CYv3FXiaclCpGN59V8XK8ipHIyi6wykO6JrSmPa0optsmH02W3'
BINANCE_API_SECRET = 'AiP11eVHbtaL73JdlGcNIsO4yaSHMSl8yhCrbRxg9Bb6qPaTPGl8og5dQMn6KMvo'
BYBIT_API_KEY = '7JeEcSvWEW7c2VGBdI'
BYBIT_API_SECRET = 'zobIPQ0YIOzkPwiDdM8A8V0P1ZmrCdAQaHZJ'

#Telegram keys
bot_token = '6394500142:AAGKgJu5SrGzz1eh_Wou-T0-NFaDuXqLH-c'
chat_id = "5274262671"

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
bybit_session = HTTP(testnet=False, api_key=BYBIT_API_KEY, api_secret=BYBIT_API_SECRET)
binance_session = requests.Session()

#global variables
fee_by, fee_bi = 0.055/100, 0.1/100
positions_open = False

## Functions

def get_bi_price(symbol):
    data = binance_session.get(f'https://api.binance.com/api/v3/ticker/bookTicker?symbol={symbol}').json()
    return float(data['bidPrice']), float(data['askPrice'])

def get_by_price(symbol):
    data = requests.get(f'https://api.bybit.com/v2/public/tickers?symbol={symbol}').json()['result'][0]
    return float(data['bid_price']), float(data['ask_price'])

def get_by_fr(symbol):
    url = f'https://api.bybit.com/v2/public/tickers?symbol={symbol}'
    data = requests.get(url).json()['result'][0]
    return float(data['funding_rate'])

def bi_order(side, quantity, trading_pair):
    return client.create_order(symbol=trading_pair, side=side, type=ORDER_TYPE_MARKET, quantity=quantity)


def by_order(side, quantity, trading_pair):
    return bybit_session.place_order(category="linear", symbol=trading_pair, side=side, orderType="Market", qty=str(quantity), timeInForce="FillOrKill", isLeverage=0)


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
            bi_bp, bi_ap = get_bi_price(trading_pair) #binance bid price and ask price
            by_bp, by_ap = get_by_price(trading_pair)
            is_ao = ((1-fee_by)*by_bp - (1+fee_bi)*bi_ap )/bi_ap > seuil_a/100
            is_to_close = (by_bp - bi_ap)/bi_ap < seuil_c/100

            if is_ao and not positions_open :
                bi_order(SIDE_BUY, quantity, trading_pair)
                by_order("Sell", quantity, trading_pair)
                print("Arbitrage opportunity detected. \n")
                telegram_bot_sendtext("Arbitrage opportunity detected, opening positions")
                positions_open = True

            elif is_to_close and positions_open:
                bi_order(SIDE_SELL, quantity, trading_pair)
                by_order("Buy", quantity, trading_pair)
                telegram_bot_sendtext("Positions closed")
                print("Positions closed. \n")
                positions_open = False

            # if positions_open :
            #     print("Waiting to close positions \n")
            #
            # elif not is_ao and not positions_open:
            #     print("No arbitrage opportunity at the moment.\n")

            # if check_for_stop_command() :
            #     telegram_bot_sendtext("Stop command received. Exiting.")
            #     print("Stop command received. Exiting. \n")
            #     break
            #time.sleep(0.5)

        except Exception as e:
            telegram_bot_sendtext(f"An error occurred: {e}")
            print(f"An error occurred: {e}")
            if str(e) == "APIError(code=-1013): Filter failure: NOTIONAL":
                break
            elif str(e)=="('Connection aborted.', OSError(50, 'Network is down'))":
                break
            elif str(e)=="('Connection aborted.', TimeoutError(60, 'Operation timed out'))":
                break
            #
