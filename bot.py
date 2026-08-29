import requests
import time
import numpy as np

# Telegram credentials
BOT_TOKEN = "8910250156:AAFXETIQy7ILusg--h5FE1PKg-dLFgS7hpg"
CHAT_ID = "7287275405"

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
def fetch_data(symbol="NILUSDT", "TUTUSDT", "STXUSDT", "COOKIEUSDT", "THEUSDT", "XAIUSDT", interval="1m", limit=100):
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    res = requests.get(BINANCE_URL, params=params).json()
    closes = [float(candle[4]) for candle in res]
    return closes

# Main Loop for multiple symbols
def run_bot(symbols, interval="1m"):
    last_signals = {sym: None for sym in symbols}
    while True:
        try:
            for sym in symbols:
                closes = fetch_data(sym, interval)
                macd, signal = calculate_macd(closes)

                if macd[-1] > signal[-1] and last_signals[sym] != "bullish":
                    send_alert(f"📈 Bullish MACD Crossover on {sym} ({interval}) | Price: {closes[-1]}")
                    last_signals[sym] = "bullish"

                elif macd[-1] < signal[-1] and last_signals[sym] != "bearish":
                    send_alert(f"📉 Bearish MACD Crossover on {sym} ({interval}) | Price: {closes[-1]}")
                    last_signals[sym] = "bearish"

            time.sleep(30)  # checks every 30 seconds
        except Exception as e:
            print("Error:", e)
            time.sleep(60)

# Run Bot
if __name__ == "__main__":
    symbols = ["NILUSDT", "TUTUSDT", "STXUSDT", "COOKIEUSDT", "THEUSDT", "XAIUSDT"]  # add more symbols here
    run_bot(symbols, "15m")  # change timeframe here
