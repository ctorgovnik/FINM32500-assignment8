#!/usr/bin/env python3
"""
Simple OrderManager Usage Example

Demonstrates starting the server and sending orders using the client library.
"""

import sys
import os
import time
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from OrderManager.server import Server
from OrderManager.client import OrderManagerClient


def run_server():
    """Run server in background thread"""
    config = {"host": "localhost", "port": 9001}
    server = Server(config)
    server.run()


def main():
    print("OrderManager Usage Example\n")
    
    # Start server in background
    print("Starting OrderManager server...")
    threading.Thread(target=run_server, daemon=True).start()
    time.sleep(1)
    
    # Create client and send orders
    print("Connecting client...")
    client = OrderManagerClient(host="localhost", port=9001)
    client.connect()
    
    print("\nSending orders:")
    
    client.place_order("AAPL", "BUY", 100, 172.53)
    print("  Sent: BUY 100 AAPL @ $172.53")
    
    client.place_order("MSFT", "SELL", 50, 325.20)
    print("  Sent: SELL 50 MSFT @ $325.20")
    
    client.place_order("GOOG", "BUY", 25, 142.50)
    print("  Sent: BUY 25 GOOG @ $142.50")
    
    time.sleep(0.5)
    
    client.disconnect()
    print("\nDone")


if __name__ == "__main__":
    main()

