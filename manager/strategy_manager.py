import asyncio

from dao.dao_strategy import strategy_dao
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
        self.intraday_moving_average_strategies = dict()

    async def register_strategy(self, strategy_type, symbol, n_currency = None, username='admin', params_opti = None, from_dao = False, optimize=True ):
        if n_currency == None:
            n_currency = self.estimate_n_currency( symbol )

        # register the symbol if it not aldready register
        if symbol not in self.symbols:
            self.symbols.append( symbol )
            await symbol_manager.register_symbol( symbol )
            await asyncio.sleep( 2 )

        if symbol not in self.moving_average_strategies:
            if strategy_type == STRATEGY_TYPE.MOVING_AVERAGE.value:
                self.moving_average_strategies[symbol]=MovingAverageStrategy( symbol, n_currency, username )
                if optimize == True:
                    if not params_opti:
                        params_opti = await self.moving_average_strategies[symbol].optimize()
                    else:
                        params_opti = await self.moving_average_strategies[symbol].optimize( params_opti )
                asyncio.create_task( self.moving_average_strategies[symbol].listen() )

        if symbol not in self.intraday_moving_average_strategies:
            if strategy_type == STRATEGY_TYPE.INTRADAY_MOVING_AVERAGE.value:
                self.intraday_moving_average_strategies[symbol]=IntradayMovingAverageStrategy( symbol, n_currency, username )
                if optimize == True:
                    if not params_opti:
                        await self.intraday_moving_average_strategies[symbol].optimize()
                    else:
                        await self.intraday_moving_average_strategies[symbol].optimize( params_opti )
                asyncio.create_task( self.intraday_moving_average_strategies[symbol].listen() )

        #Register the strategy for application restart
        if not from_dao:
            strategy_dao.insert({
                    "username":username,
                    "symbol":symbol,
                    "strategy_type":strategy_type,
                    "n_currency":n_currency,
                    "params_opti":params_opti
                })


    async def unregister_strategy(self, strategy_type, symbol, username='admin'):
        if strategy_type == STRATEGY_TYPE.MOVING_AVERAGE.name:
            if symbol in self.moving_average_strategies:
                del self.moving_average_strategies[symbol]

        if strategy_type == STRATEGY_TYPE.INTRADAY_MOVING_AVERAGE.name:
            if symbol in self.intraday_moving_average_strategies:
                del self.moving_average_strategies[symbol]

        if symbol in self.symbols and (symbol not in self.moving_average_strategies and symbol not in self.intraday_moving_average_strategies) :
            await symbol_manager.unregister_symbol( symbol, username )
            self.symbols.remove( symbol )


    async def get_registered_strategies(self):
        return {
            "moving_average_strategies":self.moving_average_strategies,
            "intraday_moving_average_strategies":self.intraday_moving_average_strategies
        }


    def estimate_n_currency(self, symbol ):
        # simply remove a fixed nb of currencies
        return 4000

strategy_managers={}