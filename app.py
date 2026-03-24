 port streamlit as st
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- PAGE CONFIG ---
st.set_page_config(page_title="Saurabh AI Scalper v11", layout="wide")

st.markdown("<h1 style='text-align:center; color:#00FFCC;'>⚡ Saurabh AI Scalping Terminal v11.0</h1>", unsafe_allow_html=True)

# 1. SCALPING WATCHLIST
WATCHLIST = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'RELIANCE.NS', 'TATASTEEL.NS', 'EURUSD=X']

def get_scalping_signal(symbol):
    try:
        # SAHI INTERVAL: Scalping ke liye 1m ya 5m zaruri hai
        df = yf.download(symbol, period="1d", interval="5m", progress=False)
        if len(df) < 30: return None
        
        # EMA Indicators
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
        
        # RSI Calculation
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain/loss)))
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Scalping Logic
        signal = "WAIT"
        if prev['EMA9'] <= prev['EMA21'] and last['EMA9'] > last['EMA21'] and last['RSI'] < 65:
            signal = "BUY 🚀"
        elif prev['EMA9'] >= prev['EMA21'] and last['EMA9'] < last['EMA21'] and last['RSI'] > 35:
            signal = "SELL 📉"
            
        return {"Symbol": symbol, "Price": round(float(last['Close']), 2), "Signal": signal, "RSI": round(float(last['RSI']),1), "DF": df}
    except: return None

# --- SCANNER BUTTON ---
if st.button("🔍 SCAN FOR INTRADAY SCALPING"):
    results = []
    with st.spinner("Finding 15-Minute Profit Opportunities..."):
        for s in WATCHLIST:
            res = get_scalping_signal(s)
            if res: results.append(res)
    
    st.subheader("🔥 Live Scalping Signals")
    for item in results:
        # Har symbol ke liye card
        with st.container():
            st.markdown(f"### {item['Symbol']} | Signal: {item['Signal']}")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Current Price", item['Price'])
            c2.metric("RSI", item['RSI'])
            
            # Entry/Target for Scalping (0.5% - 1% profit)
            entry = item['Price']
            tp = entry * 1.008 if "BUY" in item['Signal'] else entry * 0.992
            sl = entry * 0.996 if "BUY" in item['Signal'] else entry * 1.004
            
            c3.metric("TARGET", f"{tp:.2f}")
            c4.metric("STOP LOSS", f"{sl:.2f}")
            
            # Chart update for Scalping (5m candles)
            fig, ax = plt.subplots(figsize=(10, 2))
            plt.style.use('dark_background')
            plt.plot(item['DF']['Close'].tail(30), color='cyan')
            plt.title(f"{item['Symbol']} 5-Min Chart")
            st.pyplot(fig)
            st.markdown("---")
