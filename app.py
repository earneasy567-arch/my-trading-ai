import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# --- 1. SETTINGS & PERSISTENT DATA ---
YOUR_PASSWORD = "saurabh_trading"
INITIAL_FUND = 500.0

st.set_page_config(page_title="Saurabh AI Ultimate Terminal", layout="wide")

# Session State for Auth, Wallet, and History
if "auth" not in st.session_state: st.session_state.auth = False
if "balance" not in st.session_state: st.session_state.balance = INITIAL_FUND
if "active_trades" not in st.session_state: st.session_state.active_trades = []
if "history" not in st.session_state: st.session_state.history = []

if not st.session_state.auth:
    st.markdown("<h2 style='text-align:center;'>🔑 Private Access</h2>", unsafe_allow_html=True)
    val = st.text_input("Enter Password:", type="password")
    if st.button("Unlock Terminal"):
        if val == YOUR_PASSWORD:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 2. CORE MULTI-MARKET ENGINE ---
def get_market_data(symbol):
    try:
        sym = symbol.upper().strip()
        if sym == "BANKNIFTY": sym = "^NSEBANK"
        if sym == "NIFTY": sym = "^NSEI"
        
        df = yf.download(sym, period="1d", interval="1m", progress=False)
        if df.empty: return None
        
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
        
        last_p = float(df['Close'].iloc[-1])
        ema9, ema21 = df['EMA9'].iloc[-1], df['EMA21'].iloc[-1]
        sig = "BUY" if ema9 > ema21 else "SELL"
        
        # Quick Scalping Targets
        tp = round(last_p * 1.004, 2) if sig == "BUY" else round(last_p * 0.996, 2)
        sl = round(last_p * 0.998, 2) if sig == "BUY" else round(last_p * 1.002, 2)
        
        return {"sym": sym, "p": last_p, "sig": sig, "tp": tp, "sl": sl, "df": df}
    except: return None

# --- 3. UI & WALLET ---
st.sidebar.title("💰 Smart Wallet")
st.sidebar.metric("Balance", f"${st.session_state.balance:.2f}")
if st.sidebar.button("Reset All Data"):
    st.session_state.balance = INITIAL_FUND
    st.session_state.history = []
    st.session_state.active_trades = []
    st.rerun()

st.markdown("<h1 style='text-align:center; color:#00FFCC;'>⚡ Saurabh AI: Professional Trading Floor</h1>", unsafe_allow_html=True)

# Tabs Logic
tab1, tab2, tab3 = st.tabs(["🚀 Live Trading & Search", "📜 Trade History", "📈 Market Watch"])

with tab1:
    query = st.text_input("🔍 Search & Execute (e.g. BTC-USD, RELIANCE.NS, GOLD):", "")
    if query:
        res = get_market_data(query)
        if res:
            st.info(f"Analysis: {res['sym']} | Price: {res['p']} | Signal: {res['sig']}")
            if st.button(f"Start Auto-Trade for {res['sym']}"):
                st.session_state.active_trades.append({
                    "sym": res['sym'], "type": res['sig'], "entry": res['p'],
                    "tp": res['tp'], "sl": res['sl'], "time": datetime.now().strftime("%H:%M:%S")
                })
                st.success("Trade Active!")
                st.rerun()

    # --- LIVE MONITORING ---
    if st.session_state.active_trades:
        st.markdown("### 🤖 Active Positions")
        for i, trade in enumerate(st.session_state.active_trades):
            live = get_market_data(trade['sym'])
            if live:
                curr_p = live['p']
                pnl = (curr_p - trade['entry']) if trade['type'] == "BUY" else (trade['entry'] - curr_p)
                
                # Check Auto-Exit
                exit_trigger = False
                reason = ""
                if trade['type'] == "BUY":
                    if curr_p >= trade['tp']: exit_trigger, reason = True, "TARGET 🎯"
                    elif curr_p <= trade['sl']: exit_trigger, reason = True, "STOPLOSS 🛑"
                else:
                    if curr_p <= trade['tp']: exit_trigger, reason = True, "TARGET 🎯"
                    elif curr_p >= trade['sl']: exit_trigger, reason = True, "STOPLOSS 🛑"

                if exit_trigger:
                    st.session_state.balance += pnl
                    st.session_state.history.append({
                        "Time": datetime.now().strftime("%H:%M:%S"),
                        "Symbol": trade['sym'], "Type": trade['type'],
                        "PnL": round(pnl, 2), "Status": reason
                    })
                    st.session_state.active_trades.pop(i)
                    st.rerun()

                st.write(f"**{trade['sym']}** | Entry: {trade['entry']} | **Live PnL: ${pnl:.2f}**")

with tab2:
    st.subheader("📊 Your Trading Performance")
    if st.session_state.history:
        history_df = pd.DataFrame(st.session_state.history)
        st.table(history_df)
        total_p = sum(item['PnL'] for item in st.session_state.history)
        st.metric("Total Day Profit/Loss", f"${total_p:.2f}")
    else:
        st.write("No trades completed yet.")

with tab3:
    st.write("### Quick Overview")
    watchlist = ['BTC-USD', 'ETH-USD', '^NSEBANK', 'GOLD', 'EURUSD=X']
    for s in watchlist:
        r = get_market_data(s)
        if r: st.write(f"{r['sym']}: {r['p']} | {r['sig']}")
