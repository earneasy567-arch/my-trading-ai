import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# --- 1. SETTINGS & AUTH ---
YOUR_PASSWORD = "saurabh_trading"
INITIAL_FUND = 500.0

st.set_page_config(page_title="Saurabh AI Terminal v23", layout="wide")

if "auth" not in st.session_state: st.session_state.auth = False
if "balance" not in st.session_state: st.session_state.balance = INITIAL_FUND
if "active_trades" not in st.session_state: st.session_state.active_trades = []
if "history" not in st.session_state: st.session_state.history = []

if not st.session_state.auth:
    st.markdown("<h2 style='text-align:center;'>🔑 Private Access</h2>", unsafe_allow_html=True)
    val = st.text_input("Enter Password:", type="password")
    if st.button("Unlock"):
        if val == YOUR_PASSWORD:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 2. CORE ENGINE ---
def get_analysis(symbol):
    try:
        sym = symbol.upper().strip()
        if sym == "BANKNIFTY": sym = "^NSEBANK"
        if sym == "NIFTY": sym = "^NSEI"
        
        df = yf.download(sym, period="1d", interval="5m", progress=False)
        if df.empty: return None
        
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
        
        last_p = float(df['Close'].iloc[-1])
        ema9, ema21 = df['EMA9'].iloc[-1], df['EMA21'].iloc[-1]
        
        sig = "BUY 🚀" if ema9 > ema21 else "SELL 📉"
        col = "#00FF00" if ema9 > ema21 else "#FF0000"
        
        # Targets
        tp = round(last_p * 1.005, 2) if ema9 > ema21 else round(last_p * 0.995, 2)
        sl = round(last_p * 0.997, 2) if ema9 > ema21 else round(last_p * 1.003, 2)
        
        return {"sym": sym, "p": round(last_p, 2), "sig": sig, "col": col, "tp": tp, "sl": sl, "df": df}
    except: return None

# --- 3. MAIN UI ---
st.sidebar.metric("💰 Wallet Balance", f"${st.session_state.balance:.2f}")

st.markdown("<h1 style='text-align:center; color:#00FFCC;'>⚡ Saurabh AI Scalping & Auto-Trade</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚀 Live Trade", "📜 History", "⚙️ Wallet Settings"])

with tab1:
    search_query = st.text_input("🔍 Search Symbol (e.g. BTC-USD, BANKNIFTY, GOLD):", "")
    if search_query:
        res = get_analysis(search_query)
        if res:
            st.markdown(f"## {res['sym']} - <span style='color:{res['col']}'>{res['sig']}</span>", unsafe_allow_html=True)
            
            # --- PHELE JESA DISPLAY (METRICS) ---
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("LTP (Live)", res['p'])
            c2.metric("ENTRY", res['p'])
            c3.metric("TARGET", res['tp'])
            c4.metric("STOP LOSS", res['sl'])
            
            if st.button(f"🚀 Start Auto-Trade for {res['sym']}"):
                st.session_state.active_trades.append({
                    "sym": res['sym'], "type": res['sig'], "entry": res['p'],
                    "tp": res['tp'], "sl": res['sl']
                })
                st.success("Trade Activated!")
                st.rerun()

            # Chart
            fig, ax = plt.subplots(figsize=(10, 3))
            plt.style.use('dark_background')
            plt.plot(res['df']['Close'].tail(40), color='cyan')
            st.pyplot(fig)

    # Live Monitoring Section
    if st.session_state.active_trades:
        st.markdown("---")
        st.subheader("🤖 Active Positions")
        for i, t in enumerate(st.session_state.active_trades):
            live = get_analysis(t['sym'])
            if live:
                curr_p = live['p']
                pnl = (curr_p - t['entry']) if "BUY" in t['type'] else (t['entry'] - curr_p)
                
                # Auto Exit Check
                exit = False
                reason = ""
                if "BUY" in t['type']:
                    if curr_p >= t['tp']: exit, reason = True, "TARGET 🎯"
                    elif curr_p <= t['sl']: exit, reason = True, "STOPLOSS 🛑"
                else:
                    if curr_p <= t['tp']: exit, reason = True, "TARGET 🎯"
                    elif curr_p >= t['sl']: exit, reason = True, "STOPLOSS 🛑"

                if exit:
                    st.session_state.balance += pnl
                    st.session_state.history.append({"Time": datetime.now().strftime("%H:%M"), "Symbol": t['sym'], "PnL": round(pnl, 2), "Status": reason})
                    st.session_state.active_trades.pop(i)
                    st.rerun()

                
