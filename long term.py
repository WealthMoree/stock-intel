import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate

def compute_fundamental_metrics(ticker):
    # Fetch fundamental data from yfinance (limited but usable)
    stock = yf.Ticker(ticker)
    info = stock.info

    # Extract key fundamental indicators (fallback to None if missing)
    pe_ratio = info.get('forwardPE') or info.get('trailingPE')
    dividend_yield = info.get('dividendYield')
    debt_to_equity = info.get('debtToEquity')
    roe = info.get('returnOnEquity')
    eps_growth = None

    # Try to estimate EPS growth from earnings history if available
    earnings = stock.earnings
    if earnings is not None and len(earnings) >= 2:
        eps_recent = earnings['Earnings'].iloc[-1]
        eps_prev = earnings['Earnings'].iloc[-2]
        if eps_prev and eps_prev != 0:
            eps_growth = (eps_recent - eps_prev) / abs(eps_prev)

    return {
        'P/E Ratio': pe_ratio,
        'Dividend Yield': dividend_yield,
        'Debt to Equity (D/E)': debt_to_equity,
        'Return on Equity (ROE)': roe,
        'EPS Growth (most recent)': eps_growth
    }

def fundamental_check(metrics):
    # Simplistic rule-based fundamental scoring for long-term quality
    score = 0
    reasons = []

    if metrics['P/E Ratio'] is not None and metrics['P/E Ratio'] > 0 and metrics['P/E Ratio'] < 30:
        score += 1
    else:
        reasons.append("High or missing P/E ratio")

    if metrics['Debt to Equity (D/E)'] is not None and metrics['Debt to Equity (D/E)'] < 100:
        score += 1
    else:
        reasons.append("High or missing Debt-to-Equity")

    if metrics['Return on Equity (ROE)'] is not None and metrics['Return on Equity (ROE)'] > 0.15:
        score += 1
    else:
        reasons.append("Low or missing ROE")

    if metrics['EPS Growth (most recent)'] is not None and metrics['EPS Growth (most recent)'] > 0:
        score += 1
    else:
        reasons.append("Negative or missing EPS growth")

    if metrics['Dividend Yield'] is not None and metrics['Dividend Yield'] > 0:
        score += 1
    else:
        reasons.append("No or missing dividend yield")

    return score, reasons

def technical_analysis(data):
    # Calculate moving averages
    data['SMA_50'] = data['Close'].rolling(window=50).mean()
    data['SMA_200'] = data['Close'].rolling(window=200).mean()

    # Relative Strength Index - RSI
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    data['RSI'] = 100 - (100 / (1 + rs))

    # MACD
    ema_12 = data['Close'].ewm(span=12, adjust=False).mean()
    ema_26 = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = ema_12 - ema_26
    data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()

    # Support & Resistance (rolling min/max)
    data['Support'] = data['Low'].rolling(window=20, center=True).min()
    data['Resistance'] = data['High'].rolling(window=20, center=True).max()

    # Last values for decision-making
    macd_diff_prev = data['MACD'].iloc[-2] - data['Signal_Line'].iloc[-2]
    macd_diff_curr = data['MACD'].iloc[-1] - data['Signal_Line'].iloc[-1]
    rsi_current = data['RSI'].iloc[-1]
    close_current = data['Close'].iloc[-1]
    support = data['Support'].dropna().iloc[-1]
    resistance = data['Resistance'].dropna().iloc[-1]

    # Determine technical signal
    buy_signal = (macd_diff_prev < 0) and (macd_diff_curr > 0) and (rsi_current < 70)
    sell_signal = (macd_diff_prev > 0) and (macd_diff_curr < 0) and (rsi_current > 30)

    # Fallback heuristic
    if not (buy_signal or sell_signal):
        if (data['SMA_50'].iloc[-1] > data['SMA_200'].iloc[-1]) and (rsi_current < 70):
            buy_signal = True
        elif (data['SMA_50'].iloc[-1] < data['SMA_200'].iloc[-1]) and (rsi_current > 30):
            sell_signal = True

    if buy_signal:
        action = "Buy"
        entry = round(support, 2)
        target = round(resistance, 2)
        stop_loss = round(support * 0.97, 2)  # 3% below support
        duration = 180  # 6 months long-term
    elif sell_signal:
        action = "Sell"
        entry = round(resistance, 2)
        target = round(support, 2)
        stop_loss = round(resistance * 1.03, 2)  # 3% above resistance
        duration = 180
    else:
        action = "Hold"
        entry = target = stop_loss = duration = None

    return action, entry, target, stop_loss, duration, data

def plot_technical(data, ticker):
    plt.figure(figsize=(14,7))
    plt.plot(data['Close'], label="Close Price", color='black')
    plt.plot(data['SMA_50'], label="SMA 50", linestyle='--')
    plt.plot(data['SMA_200'], label="SMA 200", linestyle='--')
    plt.plot(data['Support'], label='Support', linestyle='-.', color='green')
    plt.plot(data['Resistance'], label='Resistance', linestyle='-.', color='red')
    plt.title(f"{ticker} Price with SMA and Support/Resistance")
    plt.legend()
    plt.grid(True)
    plt.show()

    plt.figure(figsize=(14,4))
    plt.plot(data['RSI'], label="RSI (14)", color='purple')
    plt.axhline(70, color='red', linestyle='--')
    plt.axhline(30, color='green', linestyle='--')
    plt.title(f"{ticker} - RSI Indicator")
    plt.legend()
    plt.grid(True)
    plt.show()

    plt.figure(figsize=(14,4))
    plt.plot(data['MACD'], label="MACD", color='blue')
    plt.plot(data['Signal_Line'], label="Signal Line", color='orange')
    plt.axhline(0, color='grey', linestyle='--')
    plt.title(f"{ticker} - MACD Indicator")
    plt.legend()
    plt.grid(True)
    plt.show()

def main():
    ticker = input("Enter stock ticker (e.g., AAPL): ").upper()

    print("\nFetching data and fundamental metrics...")
    fundamentals = compute_fundamental_metrics(ticker)
    score, reasons = fundamental_check(fundamentals)

    print("\nFundamental Metrics:")
    for k, v in fundamentals.items():
        print(f" {k}: {v if v is not None else 'N/A'}")

    print(f"\nFundamental quality score: {score}/5")
    if reasons:
        print(" Considerations:", ", ".join(reasons))
    else:
        print(" Fundamentals look solid.")

    print("\nFetching price data for technical analysis...")
    data = yf.download(ticker, period='1y', interval='1d')
    if data.empty:
        print("Failed to fetch price data.")
        return

    action, entry, target, stop_loss, duration, data = technical_analysis(data)

    print(f"\nTechnical analysis suggests: {action}")
    if action in ['Buy', 'Sell']:
        table = [[action, entry, target, stop_loss, duration]]
        headers = ["Action", "Entry Price", "Target Price", "Stop Loss", "Duration (days)"]
        print(tabulate(table, headers, tablefmt="grid"))
    else:
        print("No clear actionable trading signal detected based on technical indicators. Consider holding.")

    print("\nPlotting technical indicators...")
    plot_technical(data, ticker)

if __name__ == "__main__":
    main()

