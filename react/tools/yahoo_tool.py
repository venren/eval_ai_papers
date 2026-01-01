from typing import Dict, List
import yfinance as yf
import logging

# Optional: Set up logging for debugging
logger = logging.getLogger(__name__)


def fetch_price_data(tickers: List[str]) -> Dict[str, Dict]:
    """Fetch price and moving averages for a list of tickers using yfinance.

    Args:
        tickers: List of ticker symbols (e.g., ["AAPL", "MSFT"])

    Returns:
        Dict keyed by ticker with structure:
        {
            "AAPL": {
                "price": 150.25,           # Current market price
                "fifty_day": 148.00,       # 50-day moving average
                "two_hundred_day": 145.00, # 200-day moving average
                "raw_info": {...}         # Full yfinance info dict
            }
        }
        
        If fetching fails, ticker entry will have price=None and error message.
    """
    tickers = [t.upper() for t in tickers]
    out: Dict[str, Dict] = {}
    
    logger.debug(f"Fetching price data for {len(tickers)} tickers: {tickers}")

    # Use Tickers where available for fewer HTTP calls
    t_obj = None
    try:
        t_obj = yf.Tickers(" ".join(tickers))
        logger.debug("Successfully fetched multi-ticker data from yfinance")
    except Exception as e:
        logger.debug(f"Multi-ticker fetch failed, will retry individually: {e}")
        t_obj = None

    for t in tickers:
        try:
            tk = None
            if t_obj is not None and hasattr(t_obj, "tickers"):
                tk = t_obj.tickers.get(t)
            if tk is None:
                tk = yf.Ticker(t)

            info = tk.info or {}
            price = info.get("regularMarketPrice") or info.get("previousClose")
            fifty = info.get("fiftyDayAverage")
            two_hundred = info.get("twoHundredDayAverage")

            out[t] = {
                "price": price,
                "fifty_day": fifty,
                "two_hundred_day": two_hundred,
                "raw_info": info,
            }
        except Exception as e:
            logger.warning(f"Failed to fetch data for {t}: {str(e)}")
            out[t] = {"price": None, "fifty_day": None, "two_hundred_day": None, "error": str(e)}

    return out



