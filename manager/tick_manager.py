import asyncio

import pandas as pd
import matplotlib.pyplot as plt

from trading_client.trading_client import trading_client
from utils.singleton import Singleton
from logging_conf import log


@Singleton
class TickManager:
    def __init__(self ):
        self.symbols = []
        self.trading_client = trading_client

    async def register_symbol(self, symbol):
        if symbol not in self.symbols:
            self.symbols.append( symbol )
            asyncio.create_task(self.trading_client.follow_tick_prices(self.symbols))

    async def get_tick_datas_updated(self, symbol ):
        return await self.trading_client.get_tick_prices(symbol)

    async def get_tick_dataframe_updated(self, symbol ):
        datas = await self.get_tick_datas_updated( symbol )
        tick_prices = pd.DataFrame( list(datas.values()))
        print( tick_prices )
        tick_prices['timestamp'] = pd.to_datetime(tick_prices['timestamp'],unit='s')
        tick_prices.set_index('timestamp', inplace = True)
        tick_prices = tick_prices.sort_index()

        return tick_prices

    async def get_last_tick_data_upadted(self, symbol):
        dict_tick_prices = await self.get_tick_datas_updated()
        list_tick_prices = list( dict_tick_prices.values())
        return list_tick_prices[-1]

    async def get_tick_prices_time_delta(self, symbol, minute_timedelta = 1 ):
        return await self.trading_client.get_tick_prices_time_delta(symbol, minute_timedelta)

    async def plot_tick_prices(self, symbol, label='bid' ):
        tick_prices = await self.get_tick_dataframe_updated( symbol )
        if label in tick_prices :
            tick_prices.plot(y=label)
            plt.show()
        else:
            log.error( '[TICK_MANAGER] : %s not in tick dataframe', label )

tick_manager = TickManager.instance()