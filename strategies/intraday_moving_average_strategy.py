import asyncio
import datetime
import enum

from analyzer.moving_average_analyzer import MovingAverageAnalyzer
from strategies.base_strategy import BaseStrategy
from manager.tick_manager import TickManager
from trading_client.trading_client import TradingClient

class MODE_SELL(enum.Enum):
    ONLY_CLOSE = 0
    TAKE_SHORT = 1


class IntradayMovingAverageStrategy(BaseStrategy):

    def __init__(self, symbol, n_currencies):
        super(IntradayMovingAverageStrategy, self).__init__( symbol, n_currencies)
        self.movingAverageAnalyzer=MovingAverageAnalyzer( self.symbol, 'ema', 1, 118,1, 'intraday')
        self.optimized = False


    async def compute_signal(self ):
        signal = await self.movingAverageAnalyzer.compute_trading_signal_now()
        return signal

    async def optimize(self, params_opti = None):
        return await self.movingAverageAnalyzer.optimize( params_opti )

    def check_last_signal_too_close( self ):
        return False