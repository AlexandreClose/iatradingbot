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


class MovingAverageStrategy(BaseStrategy):

    def __init__(self, symbol, n_currencies):
        super(MovingAverageStrategy, self).__init__( symbol, n_currencies)
        self.movingAverageAnalyzer=MovingAverageAnalyzer( self.symbol, 'ema', 1, 118,1, time_type = "daily")
        self.optimized = False


    async def _compute_signal(self ):
        if not self.optimized:
            await self.movingAverageAnalyzer.optimize()
            self.optimized = True
        signal = await self.movingAverageAnalyzer.compute_trading_signal_now()
        return signal

    def check_last_signal_too_close( self ):
        return datetime.datetime.today().strftime('%Y-%m-%d') == self.last_date_signal