from datetime import datetime, timedelta
import logging
import signal
import sys
import os
import time

from trading_lib.models import MarketDataPoint
from trading_lib.strategy.price_based_strategy import MovingAverageStrategy
from trading_lib.strategy.news_based_strategy import NewsBasedStrategy

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from logger import setup_logger
from trading_lib.strategy_combiner.strategy_combiner import StrategyCombiner
from shared_memory_utils import SharedPriceBook

def run_strategy(config: dict):
    logger = setup_logger("strategy")
    logger.info("Starting Strategy process")

    try:
        strategy = configure_strategy(config)
        symbols = config["symbols"]
        shared_price_book = configure_shared_price_book(config, symbols)
        logger.info("Strategy process running")

        # Setup signal handlers
        configure_signal_handlers(logger)

        last_query_time = 0.0  # Use timestamp 0.0 instead of datetime.min

        # Keep alive
        while True:
            time.sleep(1)
            current_query_time = time.time()
            for symbol in symbols:
                price, timestamp = shared_price_book.read(symbol)
                if last_query_time < timestamp <= current_query_time:
                    strategy.got_new_price(MarketDataPoint(timestamp = timestamp, symbol = symbol, price = price))
            last_query_time = current_query_time

    except Exception as e:
        logger.error(f"Strategy error: {e}", exc_info=True)
        sys.exit(1)

def configure_signal_handlers(logger: logging.Logger):
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        logger.info("Strategy shutdown complete")
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)


def configure_shared_price_book(config: dict, symbols):
    # Strategy attaches to existing shared memory created by OrderBook
    # Retry in case OrderBook hasn't created it yet
    max_retries = 10
    retry_delay = 0.5
    logger = setup_logger("strategy")
    
    for attempt in range(max_retries):
        try:
            return SharedPriceBook(
                symbols,
                name=config.get("shared_memory_name", "order_book"),
                create=False
            )
        except FileNotFoundError:
            if attempt < max_retries - 1:
                logger.warning(f"Shared memory not found (attempt {attempt + 1}/{max_retries}). Waiting for OrderBook...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Shared memory not found after {max_retries} attempts. OrderBook may not be running.")
                raise
        except FileExistsError:
            # This shouldn't happen with create=False, but handle it just in case
            logger.warning("Shared memory exists but attach failed. Retrying...")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise

def configure_strategy(config: dict) -> StrategyCombiner:
    return StrategyCombiner(
        MovingAverageStrategy(config["short_window"], config["long_window"]),
        NewsBasedStrategy(config["bearish_threshold"], config["bullish_threshold"]),
        config)

if __name__ == "__main__":
    config = {
        "host": "localhost",
        "news_port": 8001,
        "symbols": ["AAPL", "MSFT", "GOOG"],
        "shared_memory_name": "market_prices",
        "order_manager_host": "localhost",
        "order_manager_port": 9000,
        "short_window": 5,
        "long_window": 20,
        "bullish_threshold": 60,
        "bearish_threshold": 40
    }
    
    print("Strategy Process")
    print("Press Ctrl+C to stop\n")
    
    run_strategy(config)

