import yfinance as yf
import sys
sys.path.insert(0, '..')
from schemas import WebSearchResult


def get_stock_price(ticker: str) -> WebSearchResult:
    try:
        # Clean ticker (remove potential $ sign or extra spaces)
        clean_ticker = ticker.strip().upper().replace("$", "")
        
        # Determine strict ticker symbol (LLM sometimes passes "Apple" instead of "AAPL")
        # For POC simplicity we assume the LLM passes a valid ticker or we let yfinance try
        
        stock = yf.Ticker(clean_ticker)
        info = stock.info
        
        # Fallback if no price found (sometimes yfinance returns empty info for invalid tickers)
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        
        if not current_price:
            return None
            
        currency = info.get("currency", "USD")
        name = info.get("shortName", clean_ticker)
        
        snippet = f"Current Price: {current_price} {currency}\n"
        snippet += f"Company: {name}\n"
        snippet += f"Market Cap: {info.get('marketCap', 'N/A')}\n"
        snippet += f"52 Week High: {info.get('fiftyTwoWeekHigh', 'N/A')}\n"
        snippet += f"52 Week Low: {info.get('fiftyTwoWeekLow', 'N/A')}"
        
        return WebSearchResult(
            title=f"Stock Price for {clean_ticker}",
            snippet=snippet,
            url=f"https://finance.yahoo.com/quote/{clean_ticker}"
        )
    except Exception:
        pass
        
    return None
