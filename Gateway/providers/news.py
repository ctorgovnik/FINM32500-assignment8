import random
from typing import Optional

from Gateway.providers.provider import Provider
from test.serializers import MessageSerializer

class NewsProvider(Provider):
    def __init__(self, num_sentiments: Optional[int] = None):
        self.serializer = MessageSerializer()
        self._generator = self._generate_sentiment(num_sentiments)

    def _generate_sentiment(self, num_sentiments: Optional[int] = None):
        if num_sentiments is None:
            while True:
                sentiment = random.randint(0, 100)
                yield self.serializer.add_delimiter(
                    self.serializer.serialize_sentiment(sentiment)
                )
        else:
            for _ in range(num_sentiments):
                sentiment = random.randint(0, 100)
                yield self.serializer.add_delimiter(
                    self.serializer.serialize_sentiment(sentiment)
                )

    def get_next_data(self):
        try:
            return next(self._generator)
        except StopIteration:
            return None

