import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- PAGE CONFIG ---
st.set_page_config(page_title="Saurabh AI Scalper v11.1", layout="wide")

st.markdown("<h1 style='text-align:center; color:#00FFCC;'>⚡ Saurabh AI Scalping Terminal v11.1</h1>", unsafe_allow_html=True)

# 1. WATCHLIST (Sirf Crypto rakhte hain abhi testing ke liye kyunki ye turant load hota hai)
WATCHLIST = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'DOGE-USD']

def get_scalping_signal(symbol):
    try:
        # DATA FETCH (5 Minute Interval)
        df = yf.download(symbol, period="1d", interval="5m", progress=False)
        if df.empty or len(df) < 10: 
            return None
        
        # Simple Logic for testing
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Signal Logic
        signal = "WAIT"
        if last['EMA9'] > last['EMA21']: 
            signal = "BUY 🚀"
        else:
            signal = "SELL 📉"
            
        return {"Symbol": symbol, "Price": round(float(last['Close']), 2), "Signal": signal, "DF": df}
    except Exception as e:
        return None

# --- MAIN BUTTON ---
if st.button("🔍 SCAN FOR INTRADAY SCALPING"):
    with st.spinner("Market se live data nikal raha hu..."):
        results = []
        for s in WATCHLIST:
            res = get_scalping_signal(s)
            if res:
                results.append(res)
        
        if not results:
            st.error("Data nahi mil raha! Shayad internet slow hai ya API limit hit ho gayi hai.")
        else:
            st.subheader("🔥 Live Market Data (5-Min Candles)")
            for item in results:
                # Har coin ka alag box
                with st.expander(f"{item['Symbol']} - Current Price: {item['Price']}", expanded=True):
                    c1, c2 = st.columns([1, 2])
                    
                    with c1:
                        st.write(f"### Signal: {item['Signal']}")
                        st.write(f"**Target:** {item['Price'] * 1.01:.2f}")
                        st.write(f"**Stop Loss:** {item['Price'] * 0.99:.2f}")
                    
                    with c2:
                        # Chart hamesha dikhega
                        fig, ax = plt.subplots(figsize=(8, 3))
                        plt.style.use('dark_background')
                        plt.plot(item['DF']['Close'].tail(20), color='cyan', label="Price")
                        plt.title(f"{item['Symbol']} Trend")
                        st.pyplot(fig)

