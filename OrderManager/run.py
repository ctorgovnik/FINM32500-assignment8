import signal
import sys
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from logger import setup_logger
from OrderManager.server import Server


def run_order_manager(config: dict):
    logger = setup_logger("order_manager")
    logger.info("Starting OrderManager process")
    
    try:
        server = Server(config)
        
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            server.shutdown()
            logger.info("OrderManager shutdown complete")
            sys.exit(0)
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        server.run()
        
    except Exception as e:
        logger.error(f"OrderManager error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    config = {
        "host": "localhost",
        "order_manager_port": 8500
    }
    
    print(f"OrderManager Server")
    print(f"Listening on {config['host']}:{config['order_manager_port']}")
    print("Press Ctrl+C to stop\n")
    
    run_order_manager(config)
