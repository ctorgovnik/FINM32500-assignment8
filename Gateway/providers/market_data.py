import csv

from providers.provider import Provider
from serializers import MessageSerializer

class MarketData(Provider):

    def __init__(self, data_path: str):
        self.data_path = data_path
        self.serializer = MessageSerializer()
        self._generator = self._read_csv()

    def _read_csv(self):
        with open(self.data_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                yield self.serializer.serialize_price_with_delimiter(
                        row['symbol'], 
                        row['price']
                    )

    def get_next_data(self):
        try:
            return next(self._generator)
        except StopIteration:
            return None
    