from trading_lib.strategy.news_based_strategy import NewsBasedStrategy
from trading_lib.strategy.price_based_strategy import MovingAverageStrategy
from trading_lib.strategy_combiner.strategy_combiner import StrategyCombiner
from trading_lib.models import MarketDataPoint, Action, OrderStatus, Order

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