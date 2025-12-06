import csv

from Gateway.providers.provider import Provider
from Gateway.serializers import MessageSerializer
from performance import log_performance_event

class MarketDataProvider(Provider):

    def __init__(self, data_path: str):
        self.data_path = data_path
        self.serializer = MessageSerializer()
        self._generator = self._read_csv()

    def _read_csv(self):
        while True:
            with open(self.data_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    log_performance_event(
                        component="Strategy",
                        event="trade_decision",
                        symbol=row['symbol'],
                        tick_id=row['timestamp'],
                    )
                    yield self.serializer.serialize_price_with_delimiter(
                            row['symbol'], 
                            row['price'],
                            row['timestamp']
                        )

    def get_next_data(self):
        try:
            return next(self._generator)
        except StopIteration:
            return None
    