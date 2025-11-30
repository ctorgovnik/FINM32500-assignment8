import unittest
from trading_lib.strategy.news_based_strategy import NewsBasedStrategy
from trading_lib.models import  Action

class TestNewsBasedStrategy(unittest.TestCase):
    def test_default_threshold(self):
        strategy = NewsBasedStrategy()
        self.assertEqual(strategy.generate_signal("APPL", 15), ("APPL", Action.SELL))
        self.assertEqual(strategy.generate_signal("APPL",67),  ("APPL", Action.BUY))
        self.assertEqual(strategy.generate_signal("APPL",50),  ("APPL", Action.HOLD))

    def test_custom_threshold(self):
        strategy = NewsBasedStrategy(bearish_threshold=9, bullish_threshold=14)
        self.assertEqual(strategy.generate_signal("APPL", 4),  ("APPL", Action.SELL))
        self.assertEqual(strategy.generate_signal("APPL", 10), ("APPL", Action.HOLD))
        self.assertEqual(strategy.generate_signal("APPL", 15), ("APPL", Action.BUY))
        self.assertEqual(strategy.generate_signal("APPL", 50), ("APPL", Action.BUY))
        self.assertEqual(strategy.generate_signal("APPL", 67), ("APPL", Action.BUY))

    def test_different_tickers(self):
        strategy = NewsBasedStrategy()
        self.assertEqual(strategy.generate_signal("APPL", 15), ("APPL", Action.SELL))
        self.assertEqual(strategy.generate_signal("MSFT", 67), ("MSFT", Action.BUY))
        self.assertEqual(strategy.generate_signal("IBM", 50), ("IBM", Action.HOLD))

if __name__ == '__main__':
    unittest.main()