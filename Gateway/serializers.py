
class MessageSerializer:
    """Serializes data to bytes for TCP transmission"""
    
    def __init__(self, delimiter: bytes = b'*'):
        self.delimiter = delimiter
    
    def serialize_price(self, symbol: str, price: str, timestamp: str) -> bytes:
        """Serialize price data: SYMBOL,PRICE"""
        message = f"{symbol},{price},{timestamp}"
        return message.encode('utf-8')
    
    def serialize_sentiment(self, sentiment: int) -> bytes:
        """Serialize sentiment: SENTIMENT"""
        message = str(sentiment)
        return message.encode('utf-8')
    
    def add_delimiter(self, data: bytes) -> bytes:
        """Append delimiter to message"""
        return data + self.delimiter
    
    def serialize_price_with_delimiter(self, symbol: str, price: str, timestamp: str) -> bytes:
        """Convenience method: serialize and add delimiter"""
        return self.add_delimiter(self.serialize_price(symbol, price, timestamp))