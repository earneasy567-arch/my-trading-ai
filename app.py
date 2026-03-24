import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# --- 1. SETTINGS & AUTH ---
YOUR_PASSWORD = "saurabh_trading"
st.set_page_config(page_title="Saurabh Personal AI Indicator", layout="wide")

if "auth" not in st.session_state: st.session_state.auth = False
if "balance" not in st.session_state: st.session_state.balance = 500.0
if "portfolio" not in st.session_state: st.session_state.portfolio = []
if "history" not in st.session_state: st.session_state.history = []

if not st.session_state.auth:
    st.markdown("<h2 style='text-align:center;'>🔐 Access Terminal</h2>", unsafe_allow_html=True)
    val = st.text_input("Password:", type="password")
    if st.button("Login"):
        if val == YOUR_PASSWORD:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 2. ENGINE WITH ERROR HANDLING ---
def get_analysis(symbol):
    try:
        sym = symbol.upper().strip()
        if sym == "BANKNIFTY": sym = "^NSEBANK"
        if sym == "NIFTY": sym = "^NSEI"
        
        df = yf.download(sym, period="1d", interval="5m", progress=False)
        if df.empty or len(df) < 5: return None
        
        # Technicals
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
        
        last_p = float(df['Close'].iloc[-1])
        open_p = float(df['Open'].iloc[0])
        chg = ((last_p - open_p) / open_p) * 100
        
        # S&R Logic (Robust)
        h, l = float(df['High'].max()), float(df['Low'].min())
        pivot = (h + l + last_p) / 3
        r1, s1 = (2 * pivot) - l, (2 * pivot) - h
        
        sig = "BUY 🔥" if df['EMA9'].iloc[-1] > df['EMA21'].iloc[-1] else "SELL 📉"
        col = "#00FFCC" if "BUY" in sig else "#FF4B4B"
        
        return {"sym": sym, "p": round(last_p, 2), "sig": sig, "col": col, "chg": round(chg, 2), 
                "df": df, "tp": round(last_p * 1.005, 2), "sl": round(last_p * 0.997, 2),
                "r1": r1, "s1": s1}
    except: return None

# --- 3. BRANDING HEADER ---
st.markdown(f"""
    <div style="background-color:#1E1E1E; padding:15px; border-radius:15px; border-bottom: 5px solid #00FFCC; text-align:center; margin-bottom:20px;">
        <h1 style="margin:0; color:#00FFCC; font-size:35px;">⚡ SAURABH PERSONAL AI INDICATOR v29.1</h1>
        <p style="margin:0; color:white; font-size:18px;">Automated Scalping & Trade Terminal</p>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"### 💰 Live Fund: <span style='color:#00FFCC;'>${st.session_state.balance:.2f}</span>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚀 Terminal", "🔥 Watchlist", "📜 History"])

with tab1:
    search = st.text_input("🔍 Enter Symbol (NIFTY, BANKNIFTY, BTC-USD):", "")
    if search:
        res = get_analysis(search)
        if res:
            st.markdown(f"## {res['sym']} - <span style='color:{res['col']}'>{res['sig']}</span>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("LTP", res['p'])
            c2.metric("ENTRY", res['p'])
            c3.metric("TARGET", res['tp'])
            c4.metric("STOP LOSS", res['sl'])
            
            o1, o2, o3 = st.columns([1,1,2])
            qty = o1.number_input("Qty", min_value=0.01, value=1.0)
            if o2.button("🟢 BUY Order"):
                st.session_state.portfolio.append({"sym": res['sym'], "type": "BUY", "entry": res['p'], "qty": qty, "tp": res['tp'], "sl": res['sl']})
                st.rerun()
            if o3.button("🔴 SELL Order"):
                st.session_state.portfolio.append({"sym": res['sym'], "type": "SELL", "entry": res['p'], "qty": qty, "tp": res['tp'], "sl": res['sl']})
                st.rerun()

            # Chart with Safety Check for S&R
            fig, ax = plt.subplots(figsize=(10, 4))
            plt.style.use('dark_background')
            plt.plot(res['df']['Close'].tail(50), color='cyan', label="Price", linewidth=2)
            
            # Error check: Only draw if R1/S1 are valid numbers
            if pd.notnull(res['r1']) and pd.notnull(res['s1']):
                plt.axhline(res['r1'], color='red', linestyle='--', alpha=0.7, label="Resistance")
                plt.axhline(res['s1'], color='green', linestyle='--', alpha=0.7, label="Support")
            
            plt.legend()
            st.pyplot(fig)
        else: st.error("Data loading... please wait or check symbol.")

# Active Portfolio monitoring
if st.session_state.portfolio:
    st.markdown("---")
    st.subheader("📦 Active Positions")
    for i, t in enumerate(st.session_state.portfolio):
        curr = get_analysis(t['sym'])
        if curr:
            pnl = (curr['p'] - t['entry']) * t['qty'] if t['type'] == "BUY" else (t['entry'] - curr['p']) * t['qty']
            if (t['type'] == "BUY" and (curr['p'] >= t['tp'] or curr['p'] <= t['sl'])) or \
               (t['type'] == "SELL" and (curr['p'] <= t['tp'] or curr['p'] >= t['sl'])):
                st.session_state.balance += pnl
                st.session_state.history.append({"Sym": t['sym'], "PnL": round(pnl, 2), "Time": datetime.now().strftime("%H:%M")})
                st.session_state.portfolio.pop(i)
                st.rerun()
            st.write(f"**{t['sym']}** | Live PnL: **${pnl:.2f}**")
            if st.button(f"Close Trade {i}"):
                st.session_state.balance += pnl
                st.session_state.history.append({"Sym": t['sym'], "PnL": round(pnl, 2), "Time": datetime.now().strftime("%H:%M")})
                st.session_state.portfolio.pop(i)
                st.rerun()

with tab2:
    for s in ['BTC-USD', 'ETH-USD', '^NSEBANK', 'RELIANCE.NS']:
        d = get_analysis(s)
        if d: st.write(f"{d['sym']}: {d['p']} | {d['sig']}")

with tab3:
    if st.session_state.history: st.table(pd.DataFrame(st.session_state.history))
