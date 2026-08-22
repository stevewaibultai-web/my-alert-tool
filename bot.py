import requests
import time
import yfinance as yf
import pandas as pd

# Telegram credentials
BOT_TOKEN = "8910250156 :AAFXETIQy7ILusg- -h5F E1PKg-dLFgS7hpg"
CHAT_ID = "7287275405"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram Error:", e)

def get_binance_price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        res = requests.get(url).json()
        return float(res["price"])
    except:
        return None

def get_nse_price(symbol):
    try:
        ticker = yf.Ticker(symbol + ".NS")
        data = ticker.history(period="1d")
        return float(data["Close"].iloc[-1])
    except:
        return None

def calculate_macd(prices, fast=12, slow=26, signal=9):
    series = pd.Series(prices)
    ema_fast = series.ewm(span=fast).mean()
    ema_slow = series.ewm(span=slow).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal).mean()
    return macd.iloc[-1], signal_line.iloc[-1]

def check_signal(symbol, market="binance"):
    if market == "binance":
        price = get_binance_price(symbol)
    else:
        price = get_nse_price(symbol)
    if not price:
        return None

    # Dummy price history for MACD (replace with real candles)
    prices = [price for _ in range(50)]
    macd, signal_line = calculate_macd(prices)

    if macd > signal_line:
        return f"🔔 BUY Signal on {symbol} (MACD Cross)"
    elif macd < signal_line:
        return f"🔔 SELL Signal on {symbol} (MACD Cross)"
    else:
        return None

if __name__ == "__main__":
    symbols = [
        ("BTCUSDT", "binance"),
        ("ETHUSDT", "binance"),
        ("RELIANCE", "nse"),
        ("TCS", "nse")
    ]
    while True:
        for sym, market in symbols:
            signal = check_signal(sym, market)
            if signal:
                send_telegram(signal)
                print(signal)
        time.sleep(60)  # check every minute
