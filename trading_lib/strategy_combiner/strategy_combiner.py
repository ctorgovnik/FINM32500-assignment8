from trading_lib.strategy.news_based_strategy import NewsBasedStrategy
from trading_lib.strategy.price_based_strategy import  MovingAverageStrategy
from trading_lib.models import Action, MarketDataPoint, Order
from trading_lib.strategy.base import Strategy
from OrderBook.feed_handler import FeedHandler
from logger import setup_logger
from OrderManager.client import OrderManagerClient
from trading_lib.models import Action
from typing import Optional, Callable

class StrategyCombiner:
    def __init__(self, price_strategy: MovingAverageStrategy, news_strategy: NewsBasedStrategy, config=None):
        self.price_strategy = price_strategy
        self.news_strategy = news_strategy
        self._latest_price_signal: dict[str, tuple[int, float, Action]] = {}
        self._latest_news_signal: dict[str, Action] = {}
        self._trade_signal_listener = None

        self.logger = setup_logger("StrategyCombiner")

        if config is not None:
            self.feed_handler = FeedHandler(config["host"], config["md_port"], config["news_port"])
            self.feed_handler.subscribe(self.news_listener, "news_listener")
            self.client = OrderManagerClient(config["host"], config["order_manager_port"])
            self.client.connect()
            self.set_trade_signal_listener(self._default_trade_signal_listener)

    def _default_trade_signal_listener(self, symbol: str, quantity: int, price: float, action: Action):
        """ Default callback to send order to OrderManagerClient"""
        try:
            self.client.place_order(symbol, action, quantity, price)
            self.logger.info(f"Placed order via client: symbol = {symbol}, quantity = {quantity}, price = {price}, action = {action}")
        except Exception as e:
            self.logger.error(f"Failed to place order for {symbol}: {e}")

    def shutdown(self):
        self.feed_handler.shutdown()

    def set_trade_signal_listener(self, callback: Callable[[str, int, float, Action], None]):
        """Subscribe to order status updates.

        Args:
            callback: Function to call when order status changes
        """
        self._trade_signal_listener = callback

    def deserialize_news_data(self, data: bytes) -> tuple[str, int]:
        message = data.decode('utf-8').rstrip('*').strip()
        parts = message.split(',')
        if len(parts) != 2:
            raise ValueError(f"Malformed market data (expected 2 fields, got {len(parts)}): '{message}'")

        ticker = parts[0].strip()
        try:
            sentiment = int(parts[1].strip())
        except ValueError as e:
            raise ValueError(f"Invalid sentiment '{parts[1]}' in message: '{message}'")

        if not 0 <= sentiment <= 100:
            raise ValueError(f"Expected sentiment between 0 and 100, actual value: '{parts[1]}' in message: '{message}'")

        return ticker, sentiment

    def news_listener(self, data: bytes):
        try:
            ticker, sentiment = self.deserialize_news_data(data)
        except ValueError as e:
            self.logger.error(e)
            return

        self.got_new_news(ticker, sentiment)

    def price_listener(self):
        pass

    def publish_signal(self):
        pass

    def got_new_news(self, ticker: str, news_sentiment: int):
        symbol, action = self.news_strategy.generate_signal(ticker = ticker, news_sentiment = news_sentiment)
        self._latest_news_signal[symbol] = action
        self.generate_trade_signal(ticker)

    def got_new_price(self, tick: MarketDataPoint):
        signals = self.price_strategy.generate_signals(tick = tick)

        if len(signals) == 0:
            return

        ticker, quantity, price, action = signals[0]
        self._latest_price_signal[ticker] = (quantity, price, action)

        self.generate_trade_signal(ticker)

    def generate_trade_signal(self, ticker: str):
        if ticker not in self._latest_news_signal:
            return
        if ticker not in self._latest_price_signal:
            return

        latest_price_signal = self._latest_price_signal[ticker]
        news_action = self._latest_news_signal[ticker]

        quantity, price, price_action = latest_price_signal

        if news_action == price_action:
            self._trade_signal_listener(ticker, quantity, price, price_action)

        return