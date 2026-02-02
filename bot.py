import yfinance as yf
import pandas as pd
import ta
from telegram import Bot
import time
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

def get_fibo(high, low):
    return {
        "0.0": high,
        "0.5": high - (high - low) * 0.5,
        "0.618": high - (high - low) * 0.618,
        "0.786": high - (high - low) * 0.786,
        "1.272": high + (high - low) * 0.272
    }

def analyze():
    df = yf.download("XAUUSD=X", interval="15m", period="3d")
    if df.empty:
        return None

    df['ema50'] = ta.trend.EMAIndicator(df['Close'], 50).ema_indicator()
    df['ema200'] = ta.trend.EMAIndicator(df['Close'], 200).ema_indicator()
    df['rsi'] = ta.momentum.RSIIndicator(df['Close'], 14).rsi()
    macd = ta.trend.MACD(df['Close'])
    df['macd'] = macd.macd()
    df['macds'] = macd.macd_signal()

    last = df.iloc[-1]
    high = df['High'][-50:].max()
    low = df['Low'][-50:].min()
    fibo = get_fibo(high, low)

    if last['ema50'] > last['ema200'] and last['rsi'] < 40 and last['macd'] > last['macds']:
        return f"""🟢 BUY XAUUSD
Entry: {round(fibo['0.618'],2)}
TP1: {round(fibo['0.0'],2)}
TP2: {round(fibo['1.272'],2)}
SL: {round(fibo['0.786'],2)}"""

    if last['ema50'] < last['ema200'] and last['rsi'] > 60 and last['macd'] < last['macds']:
        return f"""🔴 SELL XAUUSD
Entry: {round(fibo['0.618'],2)}
TP1: {round(fibo['0.0'],2)}
TP2: {round(fibo['1.272'],2)}
SL: {round(fibo['0.786'],2)}"""

    return None

while True:
    signal = analyze()
    if signal:
        bot.send_message(chat_id=CHAT_ID, text=signal)
        time.sleep(900)
    time.sleep(60)
