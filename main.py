import importlib.util

def run_short_term_analysis():
    short_term_path = "short term.py"
    spec = importlib.util.spec_from_file_location("short_term", short_term_path)
    short_term = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(short_term)

def run_long_term_analysis():
    long_term_path = "long  term analysis.py"
    spec = importlib.util.spec_from_file_location("long_term", long_term_path)
    long_term = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(long_term)
    long_term.main()

def main():
    ticker = input("Enter stock ticker (e.g., AAPL, INFY.NS): ").upper()
    view = input("Enter view (short/long): ").strip().lower()

    if view == "short":
        print("\n--- Running SHORT TERM Analysis ---\n")
        run_short_term_analysis()
    elif view == "long":
        print("\n--- Running LONG TERM Analysis ---\n")
        run_long_term_analysis()
    else:
        print("❌ Invalid input. Please enter 'short' or 'long'.")

if __name__ == "__main__":
    main()

