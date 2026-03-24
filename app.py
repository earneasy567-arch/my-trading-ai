import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# --- 1. SETTINGS & AUTH ---
YOUR_PASSWORD = "saurabh_trading"
st.set_page_config(page_title="Saurabh AI v27 - High Accuracy", layout="wide")

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

# --- 2. ADVANCED ANALYSIS ENGINE ---
def get_full_analysis(symbol):
    try:
        sym = symbol.upper().strip()
        if sym == "BANKNIFTY": sym = "^NSEBANK"
        if sym == "NIFTY": sym = "^NSEI"
        
        ticker = yf.Ticker(sym)
        df = ticker.history(period="1d", interval="5m")
        if df.empty: return None
        
        # Technicals
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
        
        last_p = float(df['Close'].iloc[-1])
        
        # Support/Resistance (Pivot Points)
        h, l, c = df['High'].max(), df['Low'].min(), last_p
        pivot = (h + l + c) / 3
        r1, s1 = (2 * pivot) - l, (2 * pivot) - h
        
        # Signal & Levels
        sig = "BUY 🚀" if df['EMA9'].iloc[-1] > df['EMA21'].iloc[-1] else "SELL 📉"
        col = "#00FFCC" if "BUY" in sig else "#FF4B4B"
        
        # Targets (0.5% Target, 0.3% SL)
        tp = round(last_p * 1.005, 2) if "BUY" in sig else round(last_p * 0.995, 2)
        sl = round(last_p * 0.997, 2) if "BUY" in sig else round(last_p * 1.003, 2)
        
        return {
            "sym": sym, "p": round(last_p, 2), "sig": sig, "col": col, 
            "tp": tp, "sl": sl, "r1": round(r1, 2), "s1": round(s1, 2), 
            "df": df, "news": ticker.news[:2]
        }
    except: return None

# --- 3. UI SIDEBAR ---
st.sidebar.title("💳 Saurabh Wallet")
st.sidebar.metric("Balance", f"${st.session_state.balance:.2f}")

# --- 4. TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Terminal & Trade", "📰 Market News", "📜 History"])

with tab1:
    search = st.text_input("🔍 Search Any Stock/Forex/Crypto:", "")
    if search:
        res = get_full_analysis(search)
        if res:
            # 1. HEADER & SIGNAL
            st.markdown(f"## {res['sym']} - <span style='color:{res['col']}'>{res['sig']}</span>", unsafe_allow_html=True)
            
            # 2. ENTRY, TARGET, STOP LOSS BOXES (As requested)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("LTP (Live)", res['p'])
            c2.metric("ENTRY", res['p'])
            c3.metric("TARGET 🎯", res['tp'])
            c4.metric("STOP LOSS 🛑", res['sl'])
            
            # 3. ORDER SECTION
            st.markdown("---")
            o1, o2, o3 = st.columns([1,1,2])
            qty = o1.number_input("Order Quantity", min_value=0.01, value=1.0)
            if o2.button("🟢 PLACE BUY ORDER", use_container_width=True):
                st.session_state.portfolio.append({"sym": res['sym'], "type": "BUY", "entry": res['p'], "qty": qty, "tp": res['tp'], "sl": res['sl']})
                st.success("Buy Success!")
            if o3.button("🔴 PLACE SELL ORDER", use_container_width=True):
                st.session_state.portfolio.append({"sym": res['sym'], "type": "SELL", "entry": res['p'], "qty": qty, "tp": res['tp'], "sl": res['sl']})
                st.success("Sell Success!")

            # 4. CHART WITH S&R
            fig, ax = plt.subplots(figsize=(10, 3))
            plt.style.use('dark_background')
            plt.plot(res['df']['Close'].tail(50), color='cyan', label="Price")
            plt.axhline(res['r1'], color='red', linestyle='--', alpha=0.6, label=f"Resistance: {res['r1']}")
            plt.axhline(res['s1'], color='green', linestyle='--', alpha=0.6, label=f"Support: {res['s1']}")
            plt.legend()
            st.pyplot(fig)

    # ACTIVE POSITIONS MONITORING
    if st.session_state.portfolio:
        st.markdown("### 🤖 Live Portfolio (Auto-Monitoring)")
        for i, t in enumerate(st.session_state.portfolio):
            curr = get_full_analysis(t['sym'])
            if curr:
                pnl = (curr['p'] - t['entry']) * t['qty'] if t['type'] == "BUY" else (t['entry'] - curr['p']) * t['qty']
                
                # Auto Exit Logic
                if (t['type'] == "BUY" and (curr['p'] >= t['tp'] or curr['p'] <= t['sl'])) or \
                   (t['type'] == "SELL" and (curr['p'] <= t['tp'] or curr['p'] >= t['sl'])):
                    st.session_state.balance += pnl
                    st.session_state.history.append({"Sym": t['sym'], "PnL": round(pnl, 2), "Time": datetime.now().strftime("%H:%M")})
                    st.session_state.portfolio.pop(i)
                    st.rerun()

                st.info(f"**{t['sym']}** | Entry: {t['entry']} | **Live PnL: ${pnl:.2f}**")
                if st.button(f"Manual Close {i}"):
                    st.session_state.balance += pnl
                    st.session_state.history.append({"Sym": t['sym'], "PnL": round(pnl, 2), "Time": datetime.now().strftime("%H:%M")})
                    st.session_state.portfolio.pop(i)
                    st.rerun()

with tab2:
    st.subheader("📰 Market Breaking News")
    if search:
        news_res = get_full_analysis(search)
        if news_res and news_res['news']:
            for n in news_res['news']:
                st.markdown(f"**[{n['publisher']}]**: {n['title']}")
                st.write(f"Link: {n['link']}")
                st.markdown("---")

with tab3:
    if st.session_state.history:
        st.table(pd.DataFrame(st.session_state.history))
