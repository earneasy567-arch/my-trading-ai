import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# --- 1. PRIVACY & ACCESS ---
YOUR_PASSWORD = "saurabh_trading" 

st.set_page_config(page_title="Saurabh AI Terminal v14", layout="wide")

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align:center;'>🔑 Private Access</h2>", unsafe_allow_html=True)
    val = st.text_input("Enter Password:", type="password")
    if st.button("Unlock Terminal"):
        if val == YOUR_PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Galt Password!")
    st.stop()

# --- 2. CORE ANALYSIS ENGINE ---
def get_analysis(symbol, interval="5m"):
    try:
        data = yf.download(symbol, period="1d", interval=interval, progress=False)
        if data.empty: return None
        data['EMA9'] = data['Close'].ewm(span=9, adjust=False).mean()
        data['EMA21'] = data['Close'].ewm(span=21, adjust=False).mean()
        last_p = float(data['Close'].iloc[-1])
        ema9, ema21 = float(data['EMA9'].iloc[-1]), float(data['EMA21'].iloc[-1])
        
        sig = "BUY 🚀" if ema9 > ema21 else "SELL 📉"
        col = "#00FF00" if ema9 > ema21 else "#FF0000"
        return {"sym": symbol, "p": round(last_p, 2), "sig": sig, "col": col, 
                "tp": round(last_p * 1.008, 2) if ema9 > ema21 else round(last_p * 0.992, 2),
                "sl": round(last_p * 0.996, 2) if ema9 > ema21 else round(last_p * 1.004, 2), "df": data}
    except: return None

# --- 3. MAIN UI ---
st.markdown("<h1 style='text-align:center; color:#00FFCC;'>⚡ Saurabh AI Scalping & Search Pro</h1>", unsafe_allow_html=True)

# --- 🎯 GLOBAL SEARCH BOX (Ab Yeh Saamne Hai) ---
st.markdown("### 🔍 Global Market Search")
search_query = st.text_input("Stock ya Forex symbol daalein (e.g. BTC-USD, RELIANCE.NS, EURUSD=X, GOLD):", "")

if search_query:
    res = get_analysis(search_query)
    if res:
        st.success(f"Result mil gaya: {res['sym']}")
        with st.container():
            st.markdown(f"## {res['sym']} - <span style='color:{res['col']}'>{res['sig']}</span>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("LTP", res['p'])
            c2.metric("ENTRY", res['p'])
            c3.metric("TARGET", res['tp'])
            c4.metric("STOP LOSS", res['sl'])
            
            fig, ax = plt.subplots(figsize=(10, 3))
            plt.style.use('dark_background')
            plt.plot(res['df']['Close'].tail(40), color='cyan', label="Price")
            plt.plot(res['df']['EMA9'].tail(40), color='yellow', label="EMA9")
            st.pyplot(fig)
    else:
        st.error("Symbol sahi nahi hai. Indian stocks ke liye peeche .NS lagayein (e.g. SBIN.NS)")

st.markdown("---")

# --- 4. TABS FOR WATCHLISTS ---
tab1, tab2, tab3 = st.tabs(["🇮🇳 Indian Market", "🌍 Forex/Global", "🪙 Crypto"])

def render_market(watchlist):
    if st.button(f"Scan {watchlist[0]} List"):
        for s in watchlist:
            r = get_analysis(s)
            if r:
                with st.container():
                    st.markdown(f"### {r['sym']} - <span style='color:{r['col']}'>{r['sig']}</span>", unsafe_allow_html=True)
                    cols = st.columns(4)
                    cols[0].metric("LTP", r['p'])
                    cols[1].metric("ENTRY", r['p'])
                    cols[2].metric("TARGET", r['tp'])
                    cols[3].metric("STOP LOSS", r['sl'])
                    st.markdown("---")

with tab1: render_market(['RELIANCE.NS', 'TATASTEEL.NS', 'ADANIENT.NS'])
with tab2: render_market(['EURUSD=X', 'GBPUSD=X', 'GOLD'])
with tab3: render_market(['BTC-USD', 'ETH-USD', 'SOL-USD'])

if st.sidebar.button("Logout"):
    st.session_state.auth = False
    st.rerun()
