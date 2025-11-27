import time
import signal
import sys
import os
from multiprocessing import Process
from Gateway.run import run_gateway
from config import Config

def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else 'config.json'
    config = Config(config_path)
    process = Process(target=run_gateway, args=(config.gateway,))
    
    interrupt_count = [0]
    
    def signal_handler(signum, frame):
        print(f"\n[MAIN] Received signal {signum}", flush=True)
        interrupt_count[0] += 1
        if interrupt_count[0] > 1:
            print("Force killing...", flush=True)
            if process.is_alive():
                process.kill()
            os._exit(1)
        
        print("Shutting down...", flush=True)
        if process.is_alive():
            process.terminate()
            process.join(timeout=2.0)
            if process.is_alive():
                process.kill()
        os._exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    process.start()
    
    try:
        while process.is_alive():
            try:
                signal.pause()
            except (AttributeError, OSError):
                time.sleep(0.1)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()
