import asyncio
import unittest

from manager.balance_manager import balance_manager
from manager.balance_manager import BalanceManager
from manager.historic_manager import historic_manager
from strategies.moving_average_strategy import MovingAverageStrategy
from trading_client.trading_client import trading_client


class TestBalanceManager(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestBalanceManager, self).__init__(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete( trading_client.login("11769869", "TestTest123123"))
        loop.run_until_complete( asyncio.sleep( 1 ) )
        self.balance_manager : BalanceManager = balance_manager

    def test_get_last_signal(self):
        loop = asyncio.get_event_loop()
        last_balance = loop.run_until_complete( self.balance_manager.get_last_balance() )
        self.assertIn( 'balance', last_balance)

if __name__ == '__main__':
    unittest.main()
