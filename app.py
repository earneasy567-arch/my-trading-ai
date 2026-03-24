import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# --- PAGE CONFIG ---
st.set_page_config(page_title="Saurabh AI Ultimate Scalper", layout="wide")

st.markdown("<h1 style='text-align:center; color:#00FFCC;'>⚡ Saurabh AI Scalping & Analysis Terminal</h1>", unsafe_allow_html=True)

# Function to get signals with error handling
def get_analysis(symbol, interval="5m"):
    try:
        # Scalping ke liye 1 din ka data, 5-min interval pe
        data = yf.download(symbol, period="1d", interval=interval, progress=False)
        if data.empty:
            return None
        
        # Indicators
        data['EMA9'] = data['Close'].ewm(span=9, adjust=False).mean()
        data['EMA21'] = data['Close'].ewm(span=21, adjust=False).mean()
        
        last_price = float(data['Close'].iloc[-1])
        ema9 = float(data['EMA9'].iloc[-1])
        ema21 = float(data['EMA21'].iloc[-1])
        
        # Logic
        signal = "WAIT (No Trend)"
        color = "white"
        if ema9 > ema21:
            signal = "BUY 🚀 (Bullish Trend)"
            color = "#00FF00"
        elif ema9 < ema21:
            signal = "SELL 📉 (Bearish Trend)"
            color = "#FF0000"
            
        return {
            "symbol": symbol,
            "price": round(last_price, 2),
            "signal": signal,
            "color": color,
            "tp": round(last_price * 1.01, 2) if ema9 > ema21 else round(last_price * 0.99, 2),
            "sl": round(last_price * 0.995, 2) if ema9 > ema21 else round(last_price * 1.005, 2),
            "df": data
        }
    except:
        return None

# --- UI TABS ---
tab1, tab2, tab3 = st.tabs(["🇮🇳 Indian Market", "🌍 Forex/Global", "🪙 Crypto"])

def display_market(watchlist):
    if st.button(f"Scan {watchlist[0]} & Others"):
        with st.spinner("Analyzing Market..."):
            for s in watchlist:
                res = get_analysis(s)
                if res:
                    with st.container():
                        st.markdown(f"### {res['symbol']} - <span style='color:{res['color']}'>{res['signal']}</span>", unsafe_allow_html=True)
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("LTP (Price)", res['price'])
                        c2.metric("ENTRY", res['price'])
                        c3.metric("TARGET", res['tp'])
                        c4.metric("STOP LOSS", res['sl'])
                        
                        fig, ax = plt.subplots(figsize=(10, 2))
                        plt.style.use('dark_background')
                        plt.plot(res['df']['Close'].tail(30), color='cyan', label="Price")
                        plt.plot(res['df']['EMA9'].tail(30), color='yellow', label="EMA9")
                        st.pyplot(fig)
                        st.markdown("---")
                else:
                    st.error(f"{s} ka data filhaal available nahi hai. Market closed ho sakta hai.")

with tab1:
    indian_watchlist = ['RELIANCE.NS', 'TATASTEEL.NS', 'SBIN.NS', 'INFY.NS', 'ADANIENT.NS']
    display_market(indian_watchlist)

with tab2:
    forex_watchlist = ['EURUSD=X', 'GBPUSD=X', 'JPY=X', 'GOLD']
    display_market(forex_watchlist)

with tab3:
    crypto_watchlist = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'DOGE-USD']
    display_market(crypto_watchlist)

st.sidebar.warning("Note: Indian market 3:30 PM pe band ho jata hai, uske baad signals nahi milenge.")
