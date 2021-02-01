import asyncio

from manager.manager_enums import STRATEGY_TYPE
from manager.symbol_manager import symbol_manager
from strategies.intraday_moving_average_strategy import IntradayMovingAverageStrategy
from strategies.moving_average_strategy import MovingAverageStrategy
from utils.singleton import Singleton


# Not a singleton. Depending on session
class StrategyManager:
    def __init__(self ):
        self.symbols = []
        self.moving_average_strategies = dict()

    async def register_strategy(self, strategy_type, symbol, n_currency = None, username='admin' ):

        if n_currency == None:
            n_currency = self.estimate_n_currency( symbol )

        # register the symbol if it not aldready register
        if symbol not in self.symbols:
            self.symbols.append( symbol )
            await symbol_manager.register_symbol( symbol )

            await asyncio.sleep( 3 )



            if strategy_type == STRATEGY_TYPE.MOVING_AVERAGE.value:
                self.moving_average_strategies[symbol]=MovingAverageStrategy( symbol, n_currency, username )
                asyncio.ensure_future( self.moving_average_strategies[symbol].listen() )

            if strategy_type == STRATEGY_TYPE.INTRADAY_MOVING_AVERAGE.value:

                self.moving_average_strategies[symbol]=IntradayMovingAverageStrategy( symbol, n_currency, username )
                asyncio.ensure_future( self.moving_average_strategies[symbol].listen() )
                print ( 'END ' + symbol)

    async def unregister_strategy(self, strategy_type, symbol, username='admin'):
        if symbol in self.symbols:
            await symbol_manager.unregister_symbol( symbol, username )
            self.symbols.remove( symbol )

        if strategy_type == STRATEGY_TYPE.MOVING_AVERAGE.name:
            if symbol in self.moving_average_strategies:
                del self.moving_average_strategies[symbol]




    def estimate_n_currency(self, symbol ):
        # simply remove a fixed nb of currencies
        return 4000

strategy_managers={}