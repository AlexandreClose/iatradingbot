import asyncio
import unittest

from manager.historic_manager import historic_manager
from strategies.moving_average_strategy import MovingAverageStrategy
from trading_client.trading_client import trading_client


class TestMovingAverageStrategy(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestMovingAverageStrategy, self).__init__(*args, **kwargs)
        self.symbol = 'BITCOIN'
        self.movingAverageStrategy= MovingAverageStrategy( self.symbol, 200)
        loop = asyncio.get_event_loop()
        loop.run_until_complete( trading_client.login("11769869", "TestTest123123"))
        loop.run_until_complete( historic_manager.register_symbol( self.symbol))
        loop.run_until_complete( asyncio.sleep( 3 ) )

    def test_get_last_signal(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete( self.movingAverageStrategy._get_last_signal() )

if __name__ == '__main__':
    unittest.main()
