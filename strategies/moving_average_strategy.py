import asyncio
import datetime
import enum

from analyzer.moving_average_analyzer import MovingAverageAnalyzer
from tick_manager.tick_manager import TickManager
from trading_client.trading_client import TradingClient

class MODE_SELL(enum.Enum):
    ONLY_CLOSE = 0
    TAKE_SHORT = 1


class MovingAverageStrategy:

    def __init__(self, client, symbol, n_currencies,*args, **kwargs ):
        super(MovingAverageStrategy, self).__init__(client, symbol, n_currencies,*args, **kwargs)
        self.movingAverageAnalyzer= MovingAverageAnalyzer( self.symbol, 'ema', 5, 140, True,2)

    async def _compute_signal(self ):
        signal = await self.movingAverageAnalyzer.compute_trading_signal_now()
        return signal