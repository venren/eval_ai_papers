from react.data_models.portfolio import Portfolio
from react.tools.yahoo_tool import fetch_price_data


def main():
    # initial portfolio: symbol, quantity, avg_price
    initial = [
        {"symbol": "AAPL", "quantity": 10, "avg_price": 150},
        {"symbol": "MSFT", "quantity": 5, "avg_price": 320},
        {"symbol": "TSLA", "quantity": 2, "avg_price": 200},
    ]

    p = Portfolio(initial)
    tickers = list(p.positions.keys())

    print("Fetching prices for:", tickers)
    price_data = fetch_price_data(tickers)
    # convert to simple prices dict
    prices = {t: price_data[t].get("price") for t in tickers}
    p.update_prices(prices)

    print("Portfolio state:")
    for s, info in p.to_dict().items():
        print(s, info)

    print("Total market value:", p.total_market_value())

    print("\nDetailed price data with moving averages:")
    for ticker, data in price_data.items():
        price = data.get("price")
        fifty_day = data.get("fifty_day")
        two_hundred_day = data.get("two_hundred_day")
        
        if price and fifty_day:
            ratio_50 = price / fifty_day
            print(f"  {ticker}: price={price:.2f}, 50d_avg={fifty_day:.2f}, ratio={ratio_50:.2f}")
        else:
            print(f"  {ticker}: Insufficient data")


if __name__ == "__main__":
    main()
