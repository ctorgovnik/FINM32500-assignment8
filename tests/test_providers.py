import pytest

from Gateway.providers.market_data import MarketData
from Gateway.providers.news import NewsProvider

def test_market_data_provider_reads_csv(sample_csv):
    provider = MarketData(sample_csv)
    data1 = provider.get_next_data()
    assert b"AAPL,169.89*" in data1 or data1 == b"AAPL,169.89*"
    
    data2 = provider.get_next_data()
    assert b"MSFT,320.22*" in data2 or data2 == b"MSFT,320.22*"
    
    # After exhausting the CSV, should return None
    data3 = provider.get_next_data()
    assert data3 is None

def test_market_data_provider_exhausts(sample_csv):
    provider = MarketData(sample_csv)
    data1 = provider.get_next_data()
    assert b"AAPL" in data1
    data2 = provider.get_next_data()
    assert b"MSFT" in data2
    # After reading all rows, generator should be exhausted
    data3 = provider.get_next_data()
    assert data3 is None

def test_news_provider_generates_sentiment():
    provider = NewsProvider()
    data = provider.get_next_data()
    assert data.endswith(b'*')
    sentiment_str = data.rstrip(b'*').decode('utf-8')
    sentiment = int(sentiment_str)
    assert 0 <= sentiment <= 100

def test_news_provider_continuous_generation():
    provider = NewsProvider()
    sentiments = []
    for _ in range(10):
        data = provider.get_next_data()
        sentiment_str = data.rstrip(b'*').decode('utf-8')
        sentiment = int(sentiment_str)
        sentiments.append(sentiment)
        assert 0 <= sentiment <= 100
    assert len(sentiments) == 10

