#!/usr/bin/env python3
"""
Main orchestrator for the Trading System

Starts all four processes:
- Gateway: Streams market data and news
- OrderBook: Maintains shared memory price book
- Strategy: Generates trading signals
- OrderManager: Executes orders

Usage:
    python main.py [config_file]
"""

import time
import signal
import sys
import os
from multiprocessing import Process

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from Gateway.run import run_gateway
from OrderBook.run import run_orderbook
from Strategy.run import run_strategy
from OrderManager.run import run_order_manager
from logger import setup_logger


def main():
    # Load configuration
    config_path = sys.argv[1] if len(sys.argv) > 1 else 'config.json'
    config = Config(config_path)
    
    # Setup logger
    logger = setup_logger("main")
    logger.info("Starting Trading System")
    
    print("Trading System")
    print(f"Config: {config_path}")
    print("Press Ctrl+C to stop\n")
    
    # Create processes
    processes = []
    process_info = [
        ("Gateway", run_gateway, config.gateway),
        ("OrderBook", run_orderbook, config.orderbook),
        ("Strategy", run_strategy, config.strategy),
        ("OrderManager", run_order_manager, config.ordermanager),
    ]
    
    try:
        # Start all processes
        for name, target, cfg in process_info:
            logger.info(f"Starting {name}")
            p = Process(target=target, args=(cfg,), name=name)
            p.start()
            processes.append((name, p))
            print(f"{name} started (PID: {p.pid})")
            time.sleep(0.5)  # Stagger startup
        
        print("All processes running\n")
        
        # Setup signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down")
            print("\nShutting down...")
            
            # Terminate all processes
            for name, p in processes:
                if p.is_alive():
                    logger.info(f"Stopping {name}")
                    p.terminate()
            
            # Wait for processes to terminate
            for name, p in processes:
                p.join(timeout=3.0)
                if p.is_alive():
                    logger.warning(f"{name} did not terminate, killing")
                    p.kill()
                    p.join()
            
            logger.info("Shutdown complete")
            print("Stopped")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Monitor processes
        while True:
            try:
                # Check if any process died
                for name, p in processes:
                    if not p.is_alive():
                        exit_code = p.exitcode
                        logger.error(f"{name} died (exit code: {exit_code})")
                        print(f"\n{name} died (exit code: {exit_code})")
                        signal_handler(signal.SIGTERM, None)
                
                # Sleep and check again
                time.sleep(1)
                
            except KeyboardInterrupt:
                signal_handler(signal.SIGINT, None)
                
    except Exception as e:
        logger.error(f"Main process error: {e}", exc_info=True)
        print(f"\nError: {e}")
        
        # Cleanup on error
        for name, p in processes:
            if p.is_alive():
                p.terminate()
        sys.exit(1)


if __name__ == "__main__":
    main()
