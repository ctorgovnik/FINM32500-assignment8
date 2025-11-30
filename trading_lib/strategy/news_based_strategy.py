from trading_lib.models import Action


class NewsBasedStrategy:
    """Receives news based sentiment
       returns buy,sell. or no signal based on sentiment
    """

    def __init__(self, bearish_threshold : int = 40, bullish_threshold : int = 60):
        self.bearish_threshold = bearish_threshold
        self.bullish_threshold = bullish_threshold

    def generate_signal(self, ticker: str, news_sentiment: int) -> tuple[str, Action]:
        if news_sentiment > self.bullish_threshold:
            return ticker, Action.BUY
        elif news_sentiment < self.bearish_threshold:
            return ticker, Action.SELL
        else:
            return ticker, Action.HOLD

