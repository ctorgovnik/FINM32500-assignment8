import signal
import sys
import os
import time

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from logger import setup_logger


def run_strategy(config: dict):
    logger = setup_logger("strategy")
    logger.info("Starting Strategy process")
    
    try:
        # TODO: Implement Strategy
        
        logger.info("Strategy process running (placeholder)")
        
        # Setup signal handlers
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            logger.info("Strategy shutdown complete")
            sys.exit(0)
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        # Keep alive
        while True:
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"Strategy error: {e}", exc_info=True)
        sys.exit(1)


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
    
    print("Strategy Process (Placeholder)")
    print("Press Ctrl+C to stop\n")
    
    run_strategy(config)

