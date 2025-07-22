# stock-intel
Stock-Intel is a modular Python tool that provides both short-term and long-term investment insights by combining technical and fundamental analysis. Built using yfinance, pandas, and matplotlib, this tool helps investors make data-driven decisions with visualized indicators and actionable trading signals.
## 📈 Stock View Analyzer

**Stock View Analyzer** is a Python-based tool that empowers investors with actionable insights based on their preferred investment horizon — short-term or long-term. The tool dynamically performs either technical or fundamental + technical analysis based on user input and generates a clear buy/sell/hold signal with supporting visualizations.

🔍 Features
- 📊 **Short-Term View**: Uses RSI, MACD, EMA, SMA, and support/resistance levels to identify trade setups.
- 🧮 **Long-Term View**: Combines P/E ratio, ROE, dividend yield, EPS growth, and D/E ratio with SMA and MACD for strategic decision-making.
- 📉 Generates dynamic charts using `matplotlib` for deep technical visualization.
- 🔁 Modular codebase — easy to extend with new strategies or indicators.

🚀 Technologies Used
- `Python 3.8+`
- `yfinance` – for fetching historical stock data
- `pandas` – for data processing
- `matplotlib` – for plotting indicators
- `tabulate` – for formatted console outputs

💻 How to Run

```bash
pip install -r requirements.txt
python stock_view_analysis.py
