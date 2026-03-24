s st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Trading Pro", layout="wide")

st.markdown("""
<style>
    .big-font { font-size: 30px !important; font-weight: bold; color: #1E90FF; }
    .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">⚡ Saurabh AI Trading Signals Pro v2.0</p>', unsafe_allow_html=True)
st.write("Machine Learning aur Technical Indicators se powered advanced trading website.")

# --- SEARCH SYMBOL ---
symbol = st.text_input("ENTER STOCK SYMBOL (e.g., RELIANCE.NS, TATASTEEL.NS)", "RELIANCE.NS").upper()

if st.button("RUN AI ANALYSIS"):
    with st.spinner(f"AI is analyzing {symbol}... Hang on!"):
        try:
            # 1. FETCH LIVE DATA (Last 1 Year for ML Training)
            data = yf.download(symbol, period="1y", interval="1d")
            
            if data.empty:
                st.error("Stock symbol not found! Try again.")
            else:
                # 2. DATA PREPARATION FOR MACHINE LEARNING
                df = data[['Close']].copy()
                df['Days'] = np.arange(len(df)) # X-axis variables (1, 2, 3...)
                
                # ML Logic: Linear Regression (Future Prediction)
                X = df[['Days']] # Input (Days)
                y = df['Close'] # Output (Price)
                
                model = LinearRegression()
                model.fit(X, y)
                
                # Predict for next 5 days
                future_days = np.array([[len(df) + 1], [len(df) + 2], [len(df) + 3], [len(df) + 4], [len(df) + 5]])
                future_predictions = model.predict(future_days)
                
                prediction_avg = future_predictions.mean()
                
                # 3. CALCULATE TECHNICALS (For Entry/SL)
                # RSI Manual Calculation
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                df['RSI'] = 100 - (100 / (1+rs))

                # ATR Manual Calculation
                high_low = data['High'] - data['Low']
                df['ATR'] = high_low.rolling(window=14).mean()
                
                curr_price = float(df['Close'].iloc[-1])
                rsi_val = float(df['RSI'].iloc[-1])
                atr_val = float(df['ATR'].iloc[-1]) # ATR measures volatility for accurate SL

                # --- AI RESULTS HEADER ---
                st.header("1. Machine Learning Prediction (Next 5 Days)")
                
                p_col1, p_col2 = st.columns([2, 1])
                
                with p_col1:
                    if prediction_avg > curr_price:
                        st.success(f"📈 AI BULLISH: Next 5-Day Average Prediction: ₹{prediction_avg:.2f}")
                    else:
                        st.error(f"📉 AI BEARISH: Next 5-Day Average Prediction: ₹{prediction_avg:.2f}")
                
                with p_col2:
                    st.metric("Current Price", f"₹{curr_price:.2f}")

                # --- POWERFUL SIGNALS ---
                st.header("2. Trading Signals (AI + Technicals Combined)")
                
                # Calculation Logic using Volatility (ATR)
                # Entry is slightly below current price for better risk-reward
                ideal_entry = curr_price - (atr_val * 0.2) 
                
                # Powerful Stop Loss: Using Volatility (ATR * 1.5 is standard)
                stop_loss = ideal_entry - (atr_val * 1.5)
                
                # Targets based on Risk-Reward Ratio (1:2)
                risk = ideal_entry - stop_loss
                target_1 = ideal_entry + (risk * 1.5)
                target_2 = ideal_entry + (risk * 2.5)

                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("IDEAL ENTRY", f"₹{ideal_entry:.2f}", help="Thoda wait karein is price ke liye")
                    st.info(f"Market Volatility (ATR): {atr_val:.2f}")

                with col2:
                    st.metric("TARGET 1", f"₹{target_1:.2f}")
                    st.write(f"**TARGET 2 (AI Potentail):** ₹{target_2:.2f}")

                with col3:
                    st.metric("AI STOP LOSS", f"₹{stop_loss:.2f}", help="Very Important!")
                    if rsi_val > 70:
                        st.warning(f"RSI is {rsi_val:.1f} (High Risk)")

                # --- ADVANCED CHARTING ---
                st.header("3. AI Prediction Chart")
                
                # Visualizing Prediction on Chart
                plt.figure(figsize=(10, 5))
                plt.style.use('dark_background')
                plt.plot(df['Days'][-50:], df['Close'][-50:], label="Past 50 Days Close", color='cyan')
                
                # Predicted Line
                future_x = np.arange(len(df), len(df)+5)
                plt.plot(future_x, future_predictions, label="AI Prediction", color='lime', linestyle='--', marker='o')
                
                plt.title(f"{symbol} - AI Trend Prediction")
                plt.legend()
                plt.grid(color='gray', linestyle='--', linewidth=0.3)
                st.pyplot(plt)

        except Exception as e:
            st.error(f"Stock analysis failed. Error: {e}")

st.sidebar.markdown("""
## AI Power explained:
1. **Machine Learning:** Humara model 1 saal ka stock trend sikhta hai aur Linear Regression apply karke short-term future forecast karta hai.
2. **Dynamic Stop Loss:** Hum fixed % use nahi karte. Hum ATR (Average True Range) indicator se current market 'shor' (volatility) calculate karte hain aur uske base par safer Stop Loss dete hain.
3. **AI + Technicals:** Entry tabhi safe hoti hai jab AI prediction aur Technical Indicators (RSI, ATR
