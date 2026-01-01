from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Position:
    symbol: str
    quantity: float
    avg_price: float
    current_price: Optional[float] = None

    @property
    def market_value(self) -> float:
        if self.current_price is None:
            return 0.0
        return float(self.quantity) * float(self.current_price)


class Portfolio:
    """In-memory portfolio with positions and cash management.

    Usage:
      p = Portfolio([{"symbol":"AAPL","quantity":10,"avg_price":150}])
      p.update_prices({"AAPL":170})
      print(p.total_market_value())
      print(p.total_value())  # market value + cash
    """

    def __init__(self, positions: Optional[List[Dict]] = None, initial_cash: float = 1000.0):
        self.positions: Dict[str, Position] = {}
        self.cash = float(initial_cash)
        if positions:
            for p in positions:
                self.add_position(p["symbol"], p["quantity"], p.get("avg_price", 0.0))

    def add_position(self, symbol: str, quantity: float, avg_price: float = 0.0) -> None:
        symbol = symbol.upper()
        self.positions[symbol] = Position(symbol=symbol, quantity=float(quantity), avg_price=float(avg_price))

    def buy(self, symbol: str, quantity: float, current_price: float) -> bool:
        """Buy shares. Deduct from cash. Returns True if successful."""
        cost = quantity * current_price
        if cost > self.cash:
            print(f"  ✗ Insufficient cash: need ${cost:.2f}, have ${self.cash:.2f}")
            return False
        
        self.cash -= cost
        if symbol in self.positions:
            pos = self.positions[symbol]
            total_quantity = pos.quantity + quantity
            total_cost = (pos.quantity * pos.avg_price) + cost
            pos.quantity = total_quantity
            pos.avg_price = total_cost / total_quantity
        else:
            self.add_position(symbol, quantity, current_price)
        
        print(f"  ✓ Bought {quantity} shares of {symbol} at ${current_price:.2f}")
        print(f"    Cash remaining: ${self.cash:.2f}")
        return True

    def sell(self, symbol: str, quantity: Optional[float] = None, current_price: float = 0.0) -> bool:
        """Sell shares. Add to cash. If quantity is None, sell all. Returns True if successful."""
        symbol = symbol.upper()
        if symbol not in self.positions:
            print(f"  ✗ Cannot sell {symbol} (not in portfolio)")
            return False
        
        pos = self.positions[symbol]
        sell_qty = quantity if quantity is not None else pos.quantity
        
        if sell_qty > pos.quantity:
            print(f"  ✗ Cannot sell {sell_qty} shares of {symbol} (only have {pos.quantity})")
            return False
        
        proceeds = sell_qty * current_price
        self.cash += proceeds
        
        if sell_qty == pos.quantity:
            del self.positions[symbol]
            print(f"  ✓ Sold all {pos.quantity} shares of {symbol} at ${current_price:.2f}")
        else:
            pos.quantity -= sell_qty
            print(f"  ✓ Sold {sell_qty} shares of {symbol} at ${current_price:.2f}")
        
        print(f"    Proceeds: ${proceeds:.2f}, Cash total: ${self.cash:.2f}")
        return True

    def update_prices(self, prices: Dict[str, float]) -> None:
        for sym, pos in self.positions.items():
            if sym in prices and prices[sym] is not None:
                pos.current_price = float(prices[sym])

    def total_market_value(self) -> float:
        """Value of all positions at current prices."""
        return sum(p.market_value for p in self.positions.values())

    def total_value(self) -> float:
        """Total portfolio value: positions + cash."""
        return self.total_market_value() + self.cash

    def to_dict(self) -> Dict[str, Dict]:
        out = {}
        for s, p in self.positions.items():
            out[s] = {
                "quantity": p.quantity,
                "avg_price": p.avg_price,
                "current_price": p.current_price,
                "market_value": p.market_value,
            }
        return out
