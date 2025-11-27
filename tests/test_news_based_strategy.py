import unittest
from trading_lib.strategy.news_based_strategy import NewsBasedStrategy
from trading_lib.models import  Action

class TestNewsBasedStrategy(unittest.TestCase):
    def test_default_threshold(self):
        strategy = NewsBasedStrategy()
        self.assertEqual(strategy.generate_signal(15), Action.SELL)
        self.assertEqual(strategy.generate_signal(67), Action.BUY)
        self.assertEqual(strategy.generate_signal(50), Action.HOLD)

    def test_custom_threshold(self):
        strategy = NewsBasedStrategy(threshold = 10)
        self.assertEqual(strategy.generate_signal(4), Action.SELL)
        self.assertEqual(strategy.generate_signal(10), Action.HOLD)
        self.assertEqual(strategy.generate_signal(15), Action.BUY)
        self.assertEqual(strategy.generate_signal(50), Action.BUY)
        self.assertEqual(strategy.generate_signal(67), Action.BUY)

if __name__ == '__main__':
    unittest.main()
