from unittest.mock import MagicMock
import pytest

from trading_lib.strategy.news_based_strategy import NewsBasedStrategy
from trading_lib.strategy.price_based_strategy import MovingAverageStrategy
from trading_lib.strategy_combiner.strategy_combiner import StrategyCombiner
from trading_lib.models import MarketDataPoint, Action, OrderStatus, Order

def test_news_deserialization():
    strategy_combiner = StrategyCombiner(
        price_strategy=MovingAverageStrategy(short_window=3, long_window=5, quantity=10),
        news_strategy=NewsBasedStrategy())
    ticker, sentiment = strategy_combiner.deserialize_news_data(b"MSFT,25*")
    assert ticker == "MSFT"
    assert sentiment == 25

    with pytest.raises(ValueError):
        ticker, sentiment = strategy_combiner.deserialize_news_data(b"Hi*")

    with pytest.raises(ValueError):
        ticker, sentiment = strategy_combiner.deserialize_news_data(b"Hi,Bye*")

    with pytest.raises(ValueError):
        ticker, sentiment = strategy_combiner.deserialize_news_data(b"ABCD,1000*")

    with pytest.raises(ValueError):
        ticker, sentiment = strategy_combiner.deserialize_news_data(b"ABCD,-1*")

def test_buy_buy(generate_buy_ticks):
    callback_got_called = False

    def assert_order_atrb(ticker: str, quantity: int, price: float, action: Action):
        nonlocal callback_got_called
        assert action == Action.BUY
        assert ticker == "AAPL"
        assert quantity == 10
        assert price == 110
        callback_got_called = True

    strategy_combiner = StrategyCombiner(price_strategy = MovingAverageStrategy(short_window=3, long_window=5, quantity=10),
                                         news_strategy = NewsBasedStrategy())
    strategy_combiner.set_trade_signal_listener(assert_order_atrb)

    strategy_combiner.got_new_news("AAPL", 75)
    assert not callback_got_called

    for tick_index in range(len(generate_buy_ticks) - 1):
        strategy_combiner.got_new_price(generate_buy_ticks[tick_index])
        assert not callback_got_called

    strategy_combiner.got_new_price(generate_buy_ticks[-1])
    assert callback_got_called

def test_sell_sell(generate_sell_ticks):
    callback_got_called = False

    strategy_combiner = StrategyCombiner(price_strategy = MovingAverageStrategy(short_window=3, long_window=5, quantity=10),
                                         news_strategy = NewsBasedStrategy())

    strategy_combiner.got_new_news("AAPL", 25)

    for tick_index in range(len(generate_sell_ticks) - 1):
        strategy_combiner.got_new_price(generate_sell_ticks[tick_index])

    def assert_order_atrb(ticker: str, quantity: int, price: float, action: Action):
        nonlocal callback_got_called
        assert action == Action.SELL
        assert ticker == "AAPL"
        assert quantity == 10
        assert price == 107
        callback_got_called = True

    strategy_combiner.set_trade_signal_listener(assert_order_atrb)

    strategy_combiner.got_new_price(generate_sell_ticks[-1])
    assert callback_got_called

def test_buy_price_sell_news(generate_buy_ticks):
    callback_got_called = False

    def assert_order_atrb(ticker: str, quantity: int, price: float, action: Action):
        nonlocal callback_got_called
        callback_got_called = True

    strategy_combiner = StrategyCombiner(price_strategy = MovingAverageStrategy(short_window=3, long_window=5, quantity=10),
                                         news_strategy = NewsBasedStrategy())
    strategy_combiner.set_trade_signal_listener(assert_order_atrb)

    strategy_combiner.got_new_news("AAPL", 25)
    assert not callback_got_called

    for tick in generate_buy_ticks:
        strategy_combiner.got_new_price(tick)
        assert not callback_got_called

    assert not callback_got_called

def test_sell_price_buy_news(generate_sell_ticks):
    callback_got_called = False

    def assert_order_atrb(ticker: str, quantity: int, price: float, action: Action):
        nonlocal callback_got_called
        callback_got_called = True

    strategy_combiner = StrategyCombiner(
        price_strategy=MovingAverageStrategy(short_window=3, long_window=5, quantity=10),
        news_strategy=NewsBasedStrategy())
    strategy_combiner.set_trade_signal_listener(assert_order_atrb)

    for tick in generate_sell_ticks:
        strategy_combiner.got_new_price(tick)

    assert not callback_got_called

    strategy_combiner.got_new_news("AAPL", 75)

    assert not callback_got_called

def test_init_with_config_creates_client_and_connects(monkeypatch):
    fake_client_cls = MagicMock()
    fake_client_instance = MagicMock()
    fake_client_cls.return_value = fake_client_instance
    monkeypatch.setattr(
        "trading_lib.strategy_combiner.strategy_combiner.OrderManagerClient",
        fake_client_cls,
    )

    fake_feed_cls = MagicMock()
    fake_feed_instance = MagicMock()
    fake_feed_cls.return_value = fake_feed_instance
    monkeypatch.setattr(
        "trading_lib.strategy_combiner.strategy_combiner.FeedHandler",
        fake_feed_cls,
    )

    price_strategy = MovingAverageStrategy(short_window=3, long_window=5, quantity=10)
    news_strategy = NewsBasedStrategy()

    config = {
        "host": "localhost",
        "md_port": 5000,
        "news_port": 5001,
        "order_manager_port": 6000,
    }

    combiner = StrategyCombiner(
        price_strategy=price_strategy,
        news_strategy=news_strategy,
        config=config,
    )

    fake_client_cls.assert_called_once_with("localhost", 6000)
    fake_client_instance.connect.assert_called_once()

    assert combiner._trade_signal_listener is not None


def test_generate_trade_signal_calls_client_place_order(monkeypatch):
    fake_client_cls = MagicMock()
    fake_client_instance = MagicMock()
    fake_client_cls.return_value = fake_client_instance
    monkeypatch.setattr(
        "trading_lib.strategy_combiner.strategy_combiner.OrderManagerClient",
        fake_client_cls,
    )

    fake_feed_cls = MagicMock()
    fake_feed_instance = MagicMock()
    fake_feed_cls.return_value = fake_feed_instance
    monkeypatch.setattr(
        "trading_lib.strategy_combiner.strategy_combiner.FeedHandler",
        fake_feed_cls,
    )

    price_strategy = MovingAverageStrategy(short_window=3, long_window=5, quantity=10)
    news_strategy = NewsBasedStrategy()

    config = {
        "host": "localhost",
        "md_port": 5000,
        "news_port": 5001,
        "order_manager_port": 6000,
    }

    combiner = StrategyCombiner(
        price_strategy=price_strategy,
        news_strategy=news_strategy,
        config=config,
    )

    ticker = "AAPL"
    price = 110.0
    quantity = 10
    action = Action.BUY

    combiner._latest_price_signal[ticker] = (quantity, price, action)
    combiner._latest_news_signal[ticker] = action

    combiner.generate_trade_signal(ticker)

    fake_client_instance.place_order.assert_called_once_with(
        ticker, action, quantity, price
    )
