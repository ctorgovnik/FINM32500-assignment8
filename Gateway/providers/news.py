import random
from typing import Optional

from Gateway.providers.provider import Provider
from Gateway.serializers import MessageSerializer

class NewsProvider(Provider):
    def __init__(self, config : dict, num_sentiments: Optional[int] = None):
        self.serializer = MessageSerializer()
        self._generator = self._generate_sentiment(num_sentiments)
        self.symbols = config["symbols"]
        self.num_symbols = len(self.symbols)

    def _generate_sentiment(self, num_sentiments: Optional[int] = None):
        if num_sentiments is None:
            while True:
                sentiment = random.randint(0, 100)
                symbol = self.symbols[random.randint(0, self.num_symbols - 1)]
                yield self.serializer.add_delimiter(
                    self.serializer.serialize_sentiment(symbol, sentiment)
                )
        else:
            for _ in range(num_sentiments):
                sentiment = random.randint(0, 100)
                symbol = self.symbols[random.randint(0, self.num_symbols - 1)]
                yield self.serializer.add_delimiter(
                    self.serializer.serialize_sentiment(symbol, sentiment)
                )

    def get_next_data(self):
        try:
            return next(self._generator)
        except StopIteration:
            return None

