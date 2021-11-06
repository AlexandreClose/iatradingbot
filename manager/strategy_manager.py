import asyncio

from bson import ObjectId

from dao.dao_strategy import strategy_dao
from manager.manager_enums import STRATEGY_TYPE
from manager.symbol_manager import symbol_manager
from strategies.intraday_moving_average_strategy import IntradayMovingAverageStrategy
from strategies.moving_average_strategy import MovingAverageStrategy
from utils.singleton import Singleton
from logging_conf import log


# Not a singleton. Depending on session
class StrategyManager:
    def __init__(self ):
        self.strategies = []

    async def register_strategy(self, strategy_type, symbol, n_currency = None, username='admin', params_opti = None, from_dao = False, id = None, optimize=True ):
        if n_currency == None:
            n_currency = self.estimate_n_currency( symbol )

        log.info( "[STRATEGY] Register strategy for user %s, symbol %s, type %s, and currencies %s",username,symbol,strategy_type, n_currency)


        if strategy_type == STRATEGY_TYPE.MOVING_AVERAGE.value:
            strategy = MovingAverageStrategy( symbol, n_currency, username, id= id, optimize=optimize )
        elif strategy_type == STRATEGY_TYPE.INTRADAY_MOVING_AVERAGE.value:
            strategy = IntradayMovingAverageStrategy( symbol, n_currency, username, id= id, optimize=optimize )
        await strategy.setup()
        asyncio.create_task( strategy.listen() )

        #Register the strategy for application restart
        if not from_dao:
            id_strategy_from_dao = strategy_dao.insert({
                    "username":username,
                    "symbol":symbol,
                    "strategy_type":strategy_type,
                    "n_currency":n_currency,
                    "params_opti":params_opti
                })
            strategy['id']=str(id_strategy_from_dao)
            print( strategy )
        log.info( "[STRATEGY] Append strategy for user %s with id %s",username,strategy['id'])
        self.strategies.append( strategy )
        return strategy


    async def unregister_strategy(self, strategy_type, symbol):
        self.strategies = [strat for strat in self.strategies if strat.strategy_type != strategy_type and strat.symbol != symbol]

    async def unregister_strategy_by_id(self, id):
        self.strategies = [strat for strat in self.strategies if strat.id != id]
        strategy_dao.deleteOne({'_id': ObjectId(id)})

    async def get_registered_strategies(self):
        return self.strategies


    def estimate_n_currency(self, symbol ):
        # simply remove a fixed nb of currencies
        return 4000

strategy_managers={}