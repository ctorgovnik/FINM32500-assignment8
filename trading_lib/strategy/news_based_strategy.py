from trading_lib.models import Action


class NewsBasedStrategy:
    """Receives news based sentiment
       returns buy,sell. or no signal based on sentiment
    """

    def __init__(self, threshold : int = 50):
        self.threshold = threshold

    def generate_signal(self, news_sentiment: int) -> Action:
        if news_sentiment > self.threshold:
            return Action.BUY
        elif news_sentiment < self.threshold:
            return Action.SELL
        else:
            return Action.HOLD

