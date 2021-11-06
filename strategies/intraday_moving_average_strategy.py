import asyncio
import datetime
import enum

from analyzer.moving_average_analyzer import MovingAverageAnalyzer
from strategies.base_strategy import BaseStrategy
from manager.manager_enums import STRATEGY_TYPE
from manager.tick_manager import TickManager
from trading_client.trading_client import TradingClient

class MODE_SELL(enum.Enum):
    ONLY_CLOSE = 0
    TAKE_SHORT = 1


class IntradayMovingAverageStrategy(BaseStrategy):

    def __init__(self, symbol, n_currencies, username, id = None, optimize=False, params_opti = None):
        super(IntradayMovingAverageStrategy, self).__init__( symbol, n_currencies, id = id)
        self.movingAverageAnalyzer=MovingAverageAnalyzer( self.symbol, 'ema', 1, 118,1, time_type='intraday')
        self.strategy_type = STRATEGY_TYPE.INTRADAY_MOVING_AVERAGE.value
        self.params_opti=params_opti
        if optimize:
            self.movingAverageAnalyzer.optimize( params_opti )

    async def setup(self):
        await super().setup()
        if self.optimize:
            await self.movingAverageAnalyzer.optimize(self.params_opti)


    async def compute_signal(self ):
        signal = await self.movingAverageAnalyzer.compute_trading_signal_now()
        return signal

    async def optimize(self, params_opti = None):
        return await self.movingAverageAnalyzer.optimize( params_opti )

    def check_last_signal_too_close( self ):
        return False