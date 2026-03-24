import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# --- 1. SETTINGS & AUTH ---
YOUR_PASSWORD = "saurabh_trading"
st.set_page_config(page_title="Saurabh AI Ultra Pro v25", layout="wide")

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

# --- 2. ENGINE ---
def get_data(symbol):
    try:
        sym = symbol.upper().strip()
        if sym == "BANKNIFTY": sym = "^NSEBANK"
        if sym == "NIFTY": sym = "^NSEI"
        df = yf.download(sym, period="1d", interval="5m", progress=False)
        if df.empty: return None
        
        # Strategy
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
        
        last_p = float(df['Close'].iloc[-1])
        open_p = float(df['Open'].iloc[0])
        change = ((last_p - open_p) / open_p) * 100
        
        sig = "BUY 🚀" if df['EMA9'].iloc[-1] > df['EMA21'].iloc[-1] else "SELL 📉"
        col = "#00FFCC" if sig == "BUY 🚀" else "#FF4B4B"
        
        return {"sym": sym, "p": last_p, "sig": sig, "col": col, "df": df, "chg": change}
    except: return None

# --- 3. SIDEBAR (PnL & WALLET) ---
st.sidebar.title("💳 Trading Wallet")
st.sidebar.metric("Cash Balance", f"${st.session_state.balance:.2f}")

# Live PnL Calculation
total_pnl = 0
for t in st.session_state.portfolio:
    live = get_data(t['sym'])
    if live:
        diff = (live['p'] - t['entry']) if t['type'] == "BUY" else (t['entry'] - live['p'])
        total_pnl += (diff * t['qty'])

st.sidebar.metric("Live P&L", f"${total_pnl:.2f}", delta=f"{total_pnl:.2f}")

# --- 4. TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "💻 Terminal", "📜 History"])

with tab1:
    st.subheader("🚀 Today's Market Pulse")
    
    # TOP GAINERS SECTION
    watchlist = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'RELIANCE.NS', 'GOLD', 'EURUSD=X', 'ADANIENT.NS', 'TATASTEEL.NS']
    gainer_list = []
    
    with st.spinner("Scanning Top Gainers..."):
        for s in watchlist:
            d = get_data(s)
            if d: gainer_list.append(d)
    
    # Sort by Change %
    gainer_list = sorted(gainer_list, key=lambda x: x['chg'], reverse=True)
    
    st.markdown("#### 🏆 Top Gainers (Today)")
    top_cols = st.columns(len(gainer_list[:4]))
    for i, stock in enumerate(gainer_list[:4]):
        top_cols[i].metric(stock['sym'], f"{stock['p']:.2f}", f"{stock['chg']:.2f}%")

    st.markdown("---")
    st.subheader("👀 Watchlist Signals")
    c1, c2, c3 = st.columns(3)
    # List displays
    for i, stock in enumerate(gainer_list):
        target_col = c1 if i % 3 == 0 else c2 if i % 3 == 1 else c3
        target_col.markdown(f"**{stock['sym']}**: {stock['p']} | <span style='color:{stock['col']}'>{stock['sig']}</span>", unsafe_allow_html=True)

with tab2:
    st.subheader("⚡ Professional Order Window")
    search = st.text_input("Enter Symbol to Analyze & Trade:", "")
    
    if search:
        res = get_data(search)
        if res:
            col_left, col_right = st.columns([2, 1])
            with col_left:
                st.markdown(f"### {res['sym']} | {res['sig']}")
                fig, ax = plt.subplots(figsize=(10, 4))
                plt.style.use('dark_background')
                plt.plot(res['df']['Close'].tail(50), color='cyan', linewidth=2)
                plt.title("5-Min Intraday Chart")
                st.pyplot(fig)
            
            with col_right:
                st.markdown("#### Place Order")
                qty = st.number_input("Quantity", min_value=0.01, value=1.0)
                if st.button("🟢 BUY NOW", use_container_width=True):
                    st.session_state.portfolio.append({"sym": res['sym'], "type": "BUY", "entry": res['p'], "qty": qty})
                    st.success("Buy Executed!")
                if st.button("🔴 SELL NOW", use_container_width=True):
                    st.session_state.portfolio.append({"sym": res['sym'], "type": "SELL", "entry": res['p'], "qty": qty})
                    st.success("Sell Executed!")

    # Open Positions
    if st.session_state.portfolio:
        st.markdown("### 📦 Active Positions")
        for i, t in enumerate(st.session_state.portfolio):
            curr = get_data(t['sym'])
            if curr:
                pnl = (curr['p'] - t['entry']) * t['qty'] if t['type'] == "BUY" else (t['entry'] - curr['p']) * t['qty']
                st.write(f"**{t['sym']}** | Entry: {t['entry']} | **PnL: ${pnl:.2f}**")
                if st.button(f"Close {i}"):
                    st.session_state.balance += pnl
                    st.session_state.history.append({"Symbol": t['sym'], "PnL": round(pnl, 2), "Time": datetime.now().strftime("%H:%M")})
                    st.session_state.portfolio.pop(i)
                    st.rerun()

with tab3:
    st.subheader("📜 Closed Trades Ledger")
    if st.session_state.history:
        st.table(pd.DataFrame(st.session_state.history))
        st.download_button("📥 Export History (CSV)", pd.DataFrame(st.session_state.history).to_csv(), "trades.csv")
    else: st.write("No history found.")
