import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate

# Step 1: Take user input
ticker = input("Enter stock ticker (e.g., AAPL, INFY.NS): ").upper()

# Step 2: Fetch historical data
data = yf.download(ticker, period='6mo', interval='1d')

if data.empty:
    print("Invalid stock ticker or no data found.")
    exit()

# Step 3: Calculate SMA and EMA
data['SMA_10'] = data['Close'].rolling(window=10).mean()
data['SMA_20'] = data['Close'].rolling(window=20).mean()
data['EMA_10'] = data['Close'].ewm(span=10, adjust=False).mean()
data['EMA_20'] = data['Close'].ewm(span=20, adjust=False).mean()

# Step 4: RSI
delta = data['Close'].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
avg_gain = gain.rolling(window=14).mean()
avg_loss = loss.rolling(window=14).mean()
rs = avg_gain / avg_loss
data['RSI'] = 100 - (100 / (1 + rs))

# Step 5: MACD
ema_12 = data['Close'].ewm(span=12, adjust=False).mean()
ema_26 = data['Close'].ewm(span=26, adjust=False).mean()
data['MACD'] = ema_12 - ema_26
data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()

# Step 6: Stochastic Oscillator
low_14 = data['Low'].rolling(window=14).min()
high_14 = data['High'].rolling(window=14).max()
data['%K'] = 100 * ((data['Close'] - low_14) / (high_14 - low_14))
data['%D'] = data['%K'].rolling(window=3).mean()

# --- SUPPORT AND RESISTANCE CALCULATION ---
support_window = 10  # rolling window size

data['Support'] = data['Low'].rolling(window=support_window, center=True).min()
data['Resistance'] = data['High'].rolling(window=support_window, center=True).max()

last_support = data['Support'].dropna().iloc[-1]
last_resistance = data['Resistance'].dropna().iloc[-1]

# --- CURRENT TREND ANALYSIS TO SUGGEST SINGLE ACTION ---

# Use last two MACD and Signal to detect crossover
macd_current = data['MACD'].iloc[-1]
signal_current = data['Signal_Line'].iloc[-1]
macd_prev = data['MACD'].iloc[-2]
signal_prev = data['Signal_Line'].iloc[-2]
rsi_current = data['RSI'].iloc[-1]

# Define buy signal conditions:
# MACD crossover up (macd crosses above signal) and RSI below 70 (not overbought)
buy_signal = (macd_prev < signal_prev) and (macd_current > signal_current) and (rsi_current < 70)

# Define sell signal conditions:
# MACD crossover down (macd crosses below signal) and RSI above 30 (not oversold)
sell_signal = (macd_prev > signal_prev) and (macd_current < signal_current) and (rsi_current > 30)

# Default is no clear signal: 'Hold'

if buy_signal:
    action = "Buy"
    entry = round(last_support, 2)
    target = round(last_resistance, 2)
    stop_loss = round(last_support * 0.98, 2)  # 2% below support
    duration = 30
elif sell_signal:
    action = "Sell"
    entry = round(last_resistance, 2)
    target = round(last_support, 2)
    stop_loss = round(last_resistance * 1.02, 2)  # 2% above resistance
    duration = 30
else:
    action = "Hold"
    entry = target = stop_loss = duration = None

# --- PLOTTING ---

# Chart 1: SMA with Support & Resistance
plt.figure(figsize=(14, 6))
plt.plot(data['Close'], label='Close Price', color='black', linewidth=1.5)
plt.plot(data['SMA_10'], label='SMA 10', linestyle='--', color='blue')
plt.plot(data['SMA_20'], label='SMA 20', linestyle='--', color='orange')
plt.plot(data['Support'], label='Support', linestyle='-.', color='green')
plt.plot(data['Resistance'], label='Resistance', linestyle='-.', color='red')
plt.title(f"{ticker} - SMA, Support & Resistance")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Plot other indicators as before...

# Chart 2: EMA
plt.figure(figsize=(14, 6))
plt.plot(data['Close'], label='Close Price', color='black', linewidth=1.5)
plt.plot(data['EMA_10'], label='EMA 10', linestyle=':', color='green')
plt.plot(data['EMA_20'], label='EMA 20', linestyle=':', color='red')
plt.title(f"{ticker} - EMA")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Chart 3: RSI
plt.figure(figsize=(14, 4))
plt.plot(data['RSI'], label='RSI (14)', color='purple')
plt.axhline(70, color='red', linestyle='--')
plt.axhline(30, color='green', linestyle='--')
plt.title(f"{ticker} - RSI")
plt.xlabel("Date")
plt.ylabel("RSI Value")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Chart 4: MACD
plt.figure(figsize=(14, 5))
plt.plot(data['MACD'], label='MACD')
plt.plot(data['Signal_Line'], label='Signal Line')
plt.axhline(0, color='gray', linestyle='--')
plt.title(f"{ticker} - MACD")
plt.xlabel("Date")
plt.ylabel("Value")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Chart 5: Stochastic Oscillator
plt.figure(figsize=(14, 4))
plt.plot(data['%K'], label='%K', color='darkcyan')
plt.plot(data['%D'], label='%D', color='orange')
plt.axhline(80, color='red', linestyle='--')
plt.axhline(20, color='green', linestyle='--')
plt.title(f"{ticker} - Stochastic Oscillator")
plt.xlabel("Date")
plt.ylabel("Value")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# --- PRINT SINGLE ACTION RECOMMENDATION ---

if action in ["Buy", "Sell"]:
    from tabulate import tabulate
    table = [[action, entry, target, stop_loss, duration]]
    headers = ["Action", "Entry Price", "Target Price", "Stop Loss", "Duration (days)"]
    print("\nSuggested Single Trade Action Based on Current Trend:\n")
    print(tabulate(table, headers, tablefmt="grid"))
else:
    print("\nNo clear Buy or Sell trend signal detected based on MACD and RSI. Recommendation: HOLD.\n")

