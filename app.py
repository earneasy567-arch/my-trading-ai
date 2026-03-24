import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# --- 1. PRIVACY & ACCESS ---
YOUR_PASSWORD = "saurabh_trading" 

st.set_page_config(page_title="Saurabh AI Terminal v15", layout="wide")

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

# --- 2. CORE ANALYSIS ENGINE (FOR STOCKS & INDICES) ---
def get_analysis(symbol, interval="5m"):
    try:
        # Auto-Correction for Symbols
        sym = symbol.upper().strip()
        if sym == "BANKNIFTY" or sym == "BANK NIFTY": sym = "^NSEBANK"
        if sym == "NIFTY" or sym == "NIFTY 50": sym = "^NSEI"
        
        data = yf.download(sym, period="1d", interval=interval, progress=False)
        if data.empty: return None
        
        # EMA Indicators for Scalping
        data['EMA9'] = data['Close'].ewm(span=9, adjust=False).mean()
        data['EMA21'] = data['Close'].ewm(span=21, adjust=False).mean()
        
        last_p = float(data['Close'].iloc[-1])
        ema9, ema21 = float(data['EMA9'].iloc[-1]), float(data['EMA21'].iloc[-1])
        
        sig = "BUY 🚀" if ema9 > ema21 else "SELL 📉"
        col = "#00FF00" if ema9 > ema21 else "#FF0000"
        
        # Risk Management: 0.5% Target, 0.3% SL (Scalping Standard)
        tp = round(last_p * 1.005, 2) if ema9 > ema21 else round(last_p * 0.995, 2)
        sl = round(last_p * 0.997, 2) if ema9 > ema21 else round(last_p * 1.003, 2)
        
        return {"sym": sym, "p": round(last_p, 2), "sig": sig, "col": col, "tp": tp, "sl": sl, "df": data}
    except: return None

# --- 3. MAIN UI ---
st.markdown("<h1 style='text-align:center; color:#00FFCC;'>⚡ Saurabh AI Scalping & Search Pro</h1>", unsafe_allow_html=True)

# --- 🎯 GLOBAL SEARCH BOX ---
st.markdown("### 🔍 Search Any Market (Stocks, Index, Forex)")
search_query = st.text_input("Example: BANKNIFTY, RELIANCE.NS, BTC-USD, GOLD", "")

if search_query:
    res = get_analysis(search_query)
    if res:
        with st.container():
            st.markdown(f"## {res['sym']} - <span style='color:{res['col']}'>{res['sig']}</span>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("LTP", res['p'])
            c2.metric("ENTRY", res['p'])
            c3.metric("TARGET", res['tp'])
            c4.metric("STOP LOSS", res['sl'])
            
            # Scalping Chart (1-Day View with 5m Candles)
            fig, ax = plt.subplots(figsize=(10, 3))
            plt.style.use('dark_background')
            plt.plot(res['df']['Close'].tail(40), color='cyan', label="Price")
            plt.plot(res['df']['EMA9'].tail(40), color='yellow', linewidth=1, label="EMA9")
            plt.title(f"{res['sym']} - 5 Min Scalping Chart")
            st.pyplot(fig)
    else:
        st.error("Data nahi mila! Symbol check karein (Indices ke liye ^ lagayein ya direct BANKNIFTY likhein).")

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

with tab1: render_market(['^NSEBANK', '^NSEI', 'RELIANCE.NS'])
with tab2: render_market(['EURUSD=X', 'GBPUSD=X', 'GOLD'])
with tab3: render_market(['BTC-USD', 'ETH-USD', 'SOL-USD'])
