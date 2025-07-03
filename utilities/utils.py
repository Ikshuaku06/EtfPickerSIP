import yfinance as yf

def get_current_value(symbol):
    """
    Fetches the current market value of the given ETF or stock symbol using yfinance.
    Returns the latest closing price or None if not found.
    """
    try:
        ticker = yf.Ticker(symbol+".NS")
        data = ticker.history(period="1d")
        if not data.empty:
            return data['Close'].iloc[-1]
        else:
            return None
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def get_previous_close(symbol):
    """
    Fetches the previous day's closing price for the given ETF or stock symbol using yfinance.
    Returns the previous close price or None if not found.
    """
    try:
        ticker = yf.Ticker(symbol+".NS")
        data = ticker.history(period="2d")
        if len(data) > 1:
            return data['Close'].iloc[-2]
        else:
            return None
    except Exception as e:
        print(f"Error fetching previous close for {symbol}: {e}")
        return None

if __name__ == "__main__":
    symbol = "HDFCSML250.NS"  # Example: NSE India symbol for HDFC Small Cap 250 ETF
    value = get_current_value(symbol)
    if value is not None:
        print(f"Current value of {symbol}: {value}")
    else:
        print(f"Could not fetch value for {symbol}.")
