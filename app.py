import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# --- 1. PRIVACY SETTINGS ---
# Yahan apna pasand ka password rakhein
YOUR_PASSWORD = "saurabh_trading" 

st.set_page_config(page_title="Saurabh AI Secure Terminal", layout="wide")

# Check Password
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align:center;'>🔒 Private Terminal Access</h2>", unsafe_allow_html=True)
    password_input = st.text_input("Enter Access Key:", type="password")
    if st.button("Unlock"):
        if password_input == YOUR_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Wrong Password! Access Denied.")
    st.stop() # Yahan ruk jayega jab tak password sahi na ho

# --- 2. MAIN APP STARTS HERE ---
st.markdown("<h1 style='text-align:center; color:#00FFCC;'>⚡ Saurabh AI Scalping & Search Pro</h1>", unsafe_allow_html=True)

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

# --- SEARCH OPTION ---
st.sidebar.header("🔍 Manual Search")
search_sym = st.sidebar.text_input("Enter Symbol (e.g. BTC-USD, RELIANCE.NS, EURUSD=X)")
if st.sidebar.button("Quick Analyze"):
    res = get_analysis(search_sym)
    if res:
        st.sidebar.success(f"{res['sym']}: {res['sig']}")
        st.sidebar.write(f"Price: {res['p']} | TP: {res['tp']} | SL: {res['sl']}")
    else:
        st.sidebar.error("Symbol not found!")

# --- TABS FOR MARKETS ---
tab1, tab2, tab3 = st.tabs(["🇮🇳 Indian Market", "🌍 Forex/Global", "🪙 Crypto"])

def render_market(watchlist):
    if st.button(f"Scan {watchlist[0]} List"):
        for s in watchlist:
            r = get_analysis(s)
            if r:
                with st.container():
                    st.markdown(f"### {r['sym']} - <span style='color:{r['col']}'>{r['sig']}</span>", unsafe_allow_html=True)
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("LTP", r['p'])
                    c2.metric("ENTRY", r['p'])
                    c3.metric("TARGET", r['tp'])
                    c4.metric("STOP LOSS", r['sl'])
                    fig, ax = plt.subplots(figsize=(10, 2))
                    plt.style.use('dark_background')
                    plt.plot(r['df']['Close'].tail(30), color='cyan')
                    st.pyplot(fig)
                    st.markdown("---")

with tab1: render_market(['RELIANCE.NS', 'TATASTEEL.NS', 'ADANIENT.NS'])
with tab2: render_market(['EURUSD=X', 'GBPUSD=X', 'GOLD'])
with tab3: render_market(['BTC-USD', 'ETH-USD', 'SOL-USD'])

if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.rerun()
