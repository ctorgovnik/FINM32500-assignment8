import threading

from providers.market_data import MarketDataProvider
from providers.news import NewsProvider
from stream import Stream

def run_gateway(config: dict):
    market_provider = MarketDataProvider(config["data_path"])
    md_stream = Stream(market_provider, config["md_port"], config["delimiter"])

    news_provider = NewsProvider()
    news_stream = Stream(news_provider, config["news_port"], config["delimiter"])

    threads = []
    for stream in [md_stream, news_stream]:
        thread = threading.Thread(target=stream.run, daemon=False)  # Non-daemon
        thread.start()
        threads.append(thread)

    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("Shutting down gateway...")
        for thread in threads:
            thread.join()
        exit(0)

if __name__ == "__main__":

    run_gateway({
        "data_path": "data/market_data.csv",
        "md_port": 8000,
        "news_port": 8001,
        "delimiter": b'*'
    })