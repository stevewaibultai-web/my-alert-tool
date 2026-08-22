import time
import requests

# 🤖 TELEGRAM CONFIGURATION (নিচের বক্সে আপনার আসল টোকেন ও চ্যাট আইডি দিন)
TOKEN = "8910250156 :AAFXETIQy7ILusg- -h5F E1PKg-dLFgS7hpg"  
CHAT_ID = "7287275405"  

TRACKED_SYMBOLS = [
    {"symbol": "BTCUSDT", "type": "CRYPTO", "indicator": "MACD", "timeframe": "15m", "status": "ON"},
    {"symbol": "ETHUSDT", "type": "CRYPTO", "indicator": "EMA", "timeframe": "30m", "status": "ON"},
    {"symbol": "RELIANCE.NS", "type": "STOCK", "indicator": "RSI", "timeframe": "1h", "status": "ON"},
    {"symbol": "TCS.NS", "type": "STOCK", "indicator": "MACD", "timeframe": "4h", "status": "ON"}
]

last_alerted_state = {}

def send_telegram_message(text):
    url = f"https://telegram.org{TOKEN}/sendMessage"
    try: requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except: pass

def get_crypto_price(symbol):
    try:
        res = requests.get(f"https://binance.com{symbol}", timeout=10).json()
        return float(res['price'])
    except: return None

def get_stock_price(ticker):
    try:
        res = requests.get(f"https://yahoo.com{ticker}", timeout=10).json()
        return float(res['chart']['result'][0]['meta']['regularMarketPrice'])
    except: return None

def check_indicators_and_alert():
    for item in TRACKED_SYMBOLS:
        if item["status"] == "OFF": continue
        
        symbol = item["symbol"]
        indicator = item["indicator"]
        tf = item["timeframe"]
        alert_key = f"{symbol}_{indicator}_{tf}"
        
        # Fetching price safely based on asset type
        price = get_crypto_price(symbol) if item["type"] == "CRYPTO" else get_stock_price(symbol)
        if not price: continue
        
        # TradingView API backup scanner config
        tv_sym = f"BINANCE:{symbol}" if item["type"] == "CRYPTO" else f"NSE:{symbol.replace('.NS','')}"
        url = "https://scanner.tradingview.com/global/scan"
        payload = {"symbols": {"tickers": [tv_sym]}, "columns": ["RSI", "MACD.macd", "MACD.signal", "EMA20", "EMA50"]}
        
        try:
            res = requests.post(url, json=payload, timeout=12).json()
            if "data" in res and len(res["data"]) > 0:
                tech = res["data"][0]["d"]
                rsi_val, macd_m, macd_s, ema20, ema50 = tech[0], tech[1], tech[2], tech[3], tech[4]
                
                message = ""
                if indicator == "RSI" and rsi_val:
                    if rsi_val >= 70 and last_alerted_state.get(alert_key) != "overbought":
                        message = f"🚨 RSI Overbought!\n🪙 Symbol: {symbol}\n⏱️ TF: {tf}\n💰 Price: {price}\n📊 RSI: {rsi_val:.2f}"
                        last_alerted_state[alert_key] = "overbought"
                    elif rsi_val <= 30 and last_alerted_state.get(alert_key) != "oversold":
                        message = f"🚨 RSI Oversold!\n🪙 Symbol: {symbol}\n⏱️ TF: {tf}\n💰 Price: {price}\n📊 RSI: {rsi_val:.2f}"
                        last_alerted_state[alert_key] = "oversold"
                
                elif indicator == "MACD" and macd_m and macd_s:
                    current_cross = "bullish" if macd_m > macd_s else "bearish"
                    if alert_key in last_alerted_state and last_alerted_state[alert_key] != current_cross:
                        message = f"🔔 MACD Crossover!\n🪙 Symbol: {symbol}\n⏱️ TF: {tf}\n📈 Trend: {current_cross.upper()}\n💰 Price: {price}"
                    last_alerted_state[alert_key] = current_cross
                
                elif indicator == "EMA" and ema20 and ema50:
                    current_cross = "bullish" if ema20 > ema50 else "bearish"
                    if alert_key in last_alerted_state and last_alerted_state[alert_key] != current_cross:
                        message = f"📈 EMA Crossover (20/50)!\n🪙 Symbol: {symbol}\n⏱️ TF: {tf}\n🚀 Signal: {current_cross.upper()}\n💰 Price: {price}"
                    last_alerted_state[alert_key] = current_cross
                
                if message: send_telegram_message(message)
        except: pass

if __name__ == "__main__":
    send_telegram_message("🚀 Your Trading Alert Server is now fully FIX and Running 24/7 in Background!")
    while True:
        check_indicators_and_alert()
        time.sleep(10)
        
