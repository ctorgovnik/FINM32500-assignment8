import typing

from trading_lib.strategy.base import Strategy
from trading_lib.models import MarketDataPoint, Action


class MovingAverageStrategy(Strategy):
    """
    Buys if 20-day MA > 50-day MA
    Sells if 20-day MA < 50-day MA
    """

    def __init__(self, short_window: int = 20, long_window: int = 50, quantity: int = 100):
        super().__init__(quantity)
        self.short_window = short_window
        self.long_window = long_window
        self._prices: typing.Dict[str, typing.List[float]] = {}
        # track previous MA relationship to catch true crossovers
        self._prev_short_gt_long: typing.Dict[str, bool] = {}

    def generate_signals(self, tick: MarketDataPoint) -> list[tuple[str, float, int, Action]]:
        sym, price = tick.symbol, tick.price

        if sym not in self._prices:
            self._prices[sym] = [price]
            self._prev_short_gt_long[sym] = False
            return []

        prev_prices = self._prices[sym]

        # Wait for enough prices to calculate moving averages
        if len(prev_prices) < self.long_window:
            self._prices[sym].append(price)
            return []

        short_ma = sum(prev_prices[-self.short_window:]) / self.short_window
        long_ma = sum(prev_prices[-self.long_window:]) / self.long_window

        prev_state = self._prev_short_gt_long[sym]
        curr_state = short_ma > long_ma

        signals = []
        # trigger only on transition from False -> True (crossover up)
        if (not prev_state) and curr_state:
            signals.append((sym, self.quantity, price, Action.BUY))
        if prev_state and (not curr_state):
            signals.append((sym, self.quantity, price, Action.SELL))

        self._prev_short_gt_long[sym] = curr_state

        prev_prices.append(price)
        self._prices[sym] = prev_prices[-self.long_window:]  # long_window is enough

        return signals