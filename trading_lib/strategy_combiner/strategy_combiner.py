# Reads latest prices from shared memory
# connects to gateway news stream to receive sentiment - needs ticker and sentiment
# generates trading signals buy if both buy, sell if both sell, hold otherwise
# Sends an Order message to the OrderManager when a trade is decided.
    # Manage current position (none, long, short) to avoid duplicate orders
    # Serialize orders before sending (JSON, pickle)
    # Respect MESSAGE_DELIMITER in all transmissions
# Price based strategy returns list of signals, news_based strategy returns a signal
# connect to gateway
from pkg_resources import non_empty_lines

from trading_lib.strategy.news_based_strategy import NewsBasedStrategy
from trading_lib.strategy.price_based_strategy import  MovingAverageStrategy
from trading_lib.models import Action, MarketDataPoint, Order
from trading_lib.strategy.base import Strategy
from OrderManager.client import OrderManagerClient

from typing import Optional, Callable
import config

class StrategyCombiner:
    def __init__(self, price_strategy: Strategy, news_strategy: NewsBasedStrategy):
        self.price_strategy = price_strategy
        self.news_strategy = news_strategy
        self._latest_price_signal: dict[str, tuple[float, int, Action]] = {}
        self._latest_news_signal: dict[str, Action] = {}

        self._trade_signal_listener = None

    def set_trade_signal_listener(self, callback: Callable[[str, int, float, Action], None]):
        """Subscribe to order status updates.

        Args:
            callback: Function to call when order status changes
        """
        self._trade_signal_listener = callback

    def news_listener(self):
        pass

    def price_listener(self):
        pass

    def publish_signal(self):
        pass

    def got_new_news(self, ticker: str, news_sentiment: int):
        symbol, action = self.news_strategy.generate_signal(ticker = ticker, news_sentiment = news_sentiment)
        self._latest_news_signal[symbol] = action
        return self.generate_trade_signal(ticker)

    def got_new_price(self, tick: MarketDataPoint) -> Optional[Action]:
        signals = self.price_strategy.generate_signals(tick = tick)

        if len(signals) == 0:
            return None

        ticker, price, quantity, action = signals[0]
        self._latest_price_signal[ticker] = (price, quantity, action)

        return self.generate_trade_signal(ticker)

    def generate_trade_signal(self, ticker: str) -> Optional[Action]:
        if ticker not in self._latest_news_signal:
            return None
        if ticker not in self._latest_price_signal:
            return None

        latest_price_signal = self._latest_price_signal[ticker]
        news_action = self._latest_news_signal[ticker]

        quantity, price, price_action = latest_price_signal

        if news_action == price_action:
            self._trade_signal_listener(ticker, quantity, price, price_action)

        return None






