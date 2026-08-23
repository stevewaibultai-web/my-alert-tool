import requests
import time
import numpy as np

# Telegram credentials
BOT_TOKEN = "8910250156 :AAFXETIQy7ILusg- -h5F E1PKg-dLFgS7hpg"
CHAT_ID = "7287275405"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram Error:", e

# Binance API Endpoint
BINANCE_URL = "https://api.binance.com/api/v3/klines"

# EMA Calculation
def calculate_ema(prices, period):
    ema = []
    k = 2 / (period + 1)
    ema.append(prices[0])
    for i in range(1, len(prices)):
        ema.append(prices[i] * k + ema[-1] * (1 - k))
    return np.array(ema)

# MACD Calculation
def calculate_macd(prices):
    ema_fast = calculate_ema(prices, 12)
    ema_slow = calculate_ema(prices, 26)
    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, 9)
    return macd_line, signal_line

# Telegram Alert
def send_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

# Fetch Data from Binance
def fetch_data(symbol="BTCUSDT", interval="1m", limit=100):
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    res = requests.get(BINANCE_URL, params=params).json()
    closes = [float(candle[4]) for candle in res]
    return closes

# Main Loop
def run_bot(symbol="BTCUSDT", interval="1m"):
    last_signal = None
    while True:
        try:
            closes = fetch_data(symbol, interval)
            macd, signal = calculate_macd(closes)
            
            if macd[-1] > signal[-1] and last_signal != "bullish":
                send_alert(f"📈 Bullish MACD Crossover on {symbol} ({interval}) | Price: {closes[-1]}")
                last_signal = "bullish"
            
            elif macd[-1] < signal[-1] and last_signal != "bearish":
                send_alert(f"📉 Bearish MACD Crossover on {symbol} ({interval}) | Price: {closes[-1]}")
                last_signal = "bearish"
            
            time.sleep(30)  # প্রতি ৩০ সেকেন্ডে চেক করবে
        except Exception as e:
            print("Error:", e)
            time.sleep(60)

# Run Bot
if __name__ == "__main__":
    run_bot("BTCUSDT", "1m")  # এখানে symbol আর timeframe কাস্টমাইজ করতে পারো
