import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# --- 1. SETTINGS & PERSISTENCE ---
YOUR_PASSWORD = "saurabh_trading"
st.set_page_config(page_title="Saurabh AI v28 - Pro Dashboard", layout="wide")

if "auth" not in st.session_state: st.session_state.auth = False
if "balance" not in st.session_state: st.session_state.balance = 500.0
if "portfolio" not in st.session_state: st.session_state.portfolio = []
if "history" not in st.session_state: st.session_state.history = []

if not st.session_state.auth:
    st.markdown("<h2 style='text-align:center;'>🔐 Saurabh Pro Access</h2>", unsafe_allow_html=True)
    val = st.text_input("Password:", type="password")
    if st.button("Login"):
        if val == YOUR_PASSWORD:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 2. MULTI-STRATEGY ENGINE ---
def get_analysis(symbol):
    try:
        sym = symbol.upper().strip()
        if sym == "BANKNIFTY": sym = "^NSEBANK"
        if sym == "NIFTY": sym = "^NSEI"
        
        df = yf.download(sym, period="1d", interval="5m", progress=False)
        if df.empty: return None
        
        # Strategy Indicators
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
        
        last_p = float(df['Close'].iloc[-1])
        open_p = float(df['Open'].iloc[0])
        chg = ((last_p - open_p) / open_p) * 100
        
        sig = "BUY 🔥" if df['EMA9'].iloc[-1] > df['EMA21'].iloc[-1] else "SELL 📉"
        col = "#00FFCC" if "BUY" in sig else "#FF4B4B"
        
        # Targets
        tp = round(last_p * 1.005, 2) if "BUY" in sig else round(last_p * 0.995, 2)
        sl = round(last_p * 0.997, 2) if "BUY" in sig else round(last_p * 1.003, 2)
        
        return {"sym": sym, "p": round(last_p, 2), "sig": sig, "col": col, "tp": tp, "sl": sl, "chg": round(chg, 2), "df": df}
    except: return None

# --- 3. FRONT PAGE UI ---
# Top Header: Wallet Status
st.markdown(f"""
    <div style="background-color:#1E1E1E; padding:20px; border-radius:15px; border-left: 10px solid #00FFCC; margin-bottom:20px;">
        <h1 style="margin:0; color:white;">💰 Total Trading Fund: <span style="color:#00FFCC;">${st.session_state.balance:.2f}</span></h1>
        <p style="margin:0; color:#AAAAAA;">Live Profit/Loss will be added/deducted automatically after trade close.</p>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 Dashboard & Trade", "📰 News", "📜 History"])

with tab1:
    # --- WATCHLIST / PUMP SECTION ---
    st.subheader("🔥 Market Watchlist (Top Gainers & Signals)")
    w_cols = st.columns(3)
    
    # 1. Crypto Watch
    with w_cols[0]:
        st.markdown("### 🪙 Crypto")
        for s in ['BTC-USD', 'ETH-USD', 'SOL-USD', 'DOGE-USD']:
            d = get_analysis(s)
            if d: st.markdown(f"**{d['sym']}**: {d['p']} | <span style='color:{d['col']}'>{d['chg']}% {d['sig']}</span>", unsafe_allow_html=True)

    # 2. Forex / Gold Watch
    with w_cols[1]:
        st.markdown("### 🌍 Forex & Global")
        for s in ['EURUSD=X', 'GBPUSD=X', 'GOLD', 'SILVER']:
            d = get_analysis(s)
            if d: st.markdown(f"**{d['sym']}**: {d['p']} | <span style='color:{d['col']}'>{d['chg']}% {d['sig']}</span>", unsafe_allow_html=True)

    # 3. Indian Stocks Watch
    with w_cols[2]:
        st.markdown("### 🇮🇳 Indian Stocks")
        for s in ['^NSEBANK', 'RELIANCE.NS', 'TATASTEEL.NS', 'ADANIENT.NS']:
            d = get_analysis(s)
            if d: st.markdown(f"**{d['sym']}**: {d['p']} | <span style='color:{d['col']}'>{d['chg']}% {d['sig']}</span>", unsafe_allow_html=True)

    st.markdown("---")
    
    # --- SEARCH & TRADE ---
    st.subheader("🔍 Analyze & Execute Trade")
    search = st.text_input("Enter Symbol to Open Terminal:", "")
    if search:
        res = get_analysis(search)
        if res:
            st.markdown(f"## {res['sym']} Terminal")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("LTP", res['p'])
            c2.metric("ENTRY", res['p'])
            c3.metric("TARGET", res['tp'])
            c4.metric("STOP LOSS", res['sl'])
            
            o1, o2, o3 = st.columns([1,1,2])
            qty = o1.number_input("Quantity", min_value=0.01, value=1.0)
            if o2.button("🟢 BUY Order", use_container_width=True):
                st.session_state.portfolio.append({"sym": res['sym'], "type": "BUY", "entry": res['p'], "qty": qty, "tp": res['tp'], "sl": res['sl']})
                st.rerun()
            if o3.button("🔴 SELL Order", use_container_width=True):
                st.session_state.portfolio.append({"sym": res['sym'], "type": "SELL", "entry": res['p'], "qty": qty, "tp": res['tp'], "sl": res['sl']})
                st.rerun()

    # --- LIVE PORTFOLIO ---
    if st.session_state.portfolio:
        st.markdown("### 🤖 Your Active Positions")
        for i, t in enumerate(st.session_state.portfolio):
            curr = get_analysis(t['sym'])
            if curr:
                pnl = (curr['p'] - t['entry']) * t['qty'] if t['type'] == "BUY" else (t['entry'] - curr['p']) * t['qty']
                
                # Auto Exit Check
                if (t['type'] == "BUY" and (curr['p'] >= t['tp'] or curr['p'] <= t['sl'])) or \
                   (t['type'] == "SELL" and (curr['p'] <= t['tp'] or curr['p'] >= t['sl'])):
                    st.session_state.balance += pnl
                    st.session_state.history.append({"Sym": t['sym'], "PnL": round(pnl, 2), "Time": datetime.now().strftime("%H:%M")})
                    st.session_state.portfolio.pop(i)
                    st.rerun()

                st.info(f"**{t['sym']}** | Entry: {t['entry']} | **Live PnL: ${pnl:.2f}**")
                if st.button(f"Manual Exit {i}"):
                    st.session_state.balance += pnl
                    st.session_state.history.append({"Sym": t['sym'], "PnL": round(pnl, 2), "Time": datetime.now().strftime("%H:%M")})
                    st.session_state.portfolio.pop(i)
                    st.rerun()

# --- OTHER TABS (News & History) ---
with tab2:
    st.write("Latest News for searched symbol will appear here.")
with tab3:
    if st.session_state.history:
        st.table(pd.DataFrame(st.session_state.history))
                
