import os
import sys
import threading
import signal

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from logger import setup_logger
from Gateway.providers.market_data import MarketDataProvider
from Gateway.providers.news import NewsProvider
from Gateway.stream import Stream

def run_gateway(config: dict):
    logger = setup_logger("gateway")
    logger.info("Starting Gateway process")
    
    try:
        market_provider = MarketDataProvider(config["data_path"])
    except Exception as e:
        logger.error(f"Failed to initialize market data provider: {e}", exc_info=True)
        return
    
    md_stream = Stream(market_provider, config["md_port"], config["delimiter"], logger)
    news_provider = NewsProvider(config = config)
    news_stream = Stream(news_provider, config["news_port"], config["delimiter"], logger)

    for stream in [md_stream, news_stream]:
        threading.Thread(target=stream.run, daemon=True).start()

    def shutdown():
        logger.info("Shutting down gateway...")
        for stream in [md_stream, news_stream]:
            stream.shutdown()
        logger.info("Gateway shutdown complete")
    
    def signal_handler(signum, frame):
        logger.info(f"[GATEWAY] Received signal {signum}")
        shutdown()
        os._exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    import time
    try:
        while True:
            try:
                signal.pause()
            except (AttributeError, OSError):
                time.sleep(0.1)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    run_gateway({
        "data_path": "data/market_data.csv",
        "md_port": 8000,
        "news_port": 8001,
        "delimiter": b'*',
        "symbols": ["AAPL", "MSFT", "SPY"]
    })
