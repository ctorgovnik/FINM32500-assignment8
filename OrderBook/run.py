import signal
import sys
import os
import time

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from logger import setup_logger
from OrderBook.order_book import OrderBook


def run_orderbook(config: dict):
    logger = setup_logger("orderbook")
    logger.info("Starting OrderBook process")
    
    try:
        # Create OrderBook instance (handles feed handler, shared memory, etc.)
        order_book = OrderBook(config)
        
        # Setup signal handlers
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            try:
                order_book.shutdown()
            except:
                pass
            try:
                order_book.shared_price_book.close()
                order_book.shared_price_book.unlink()
            except:
                pass
            logger.info("OrderBook shutdown complete")
            sys.exit(0)
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        # Start listening 
        logger.info("OrderBook listening for market data...")
        order_book.run()
        
        # Keep alive
        while True:
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"OrderBook error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    import time
    
    config = {
        "host": "localhost",
        "md_port": 8000,
        "news_port": 8001,
        "symbols": ["AAPL", "MSFT", "GOOG"],
        "shared_memory_name": "market_prices"
    }
    
    print(f"OrderBook Process")
    print(f"Connecting to Gateway at {config['host']}:{config['md_port']}")
    print("Press Ctrl+C to stop\n")
    
    run_orderbook(config)

