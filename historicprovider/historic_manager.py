import asyncio

import pandas as pd
import matplotlib.pyplot as plt
from logging_conf import log

from dao.mongodb_client_history import MongoDbClientHistory

class HistoricManager():
    def __init__(self, loop, symbols,*providers):
        self.datas = []
        self.clientMongos = { symbol: MongoDbClientHistory( symbols) for symbol in symbols }
        self.providers=providers
        self.symbols = symbols
        self.historical_datas = { symbol : [] for symbol in symbols }
        loop.run_until_complete( self.fetch_and_store_max_history( ) )
        loop.create_task(self.fetch_and_store_max_history_loop( ) )

    async def get_historical_datas_updated(self, symbol ):
        if self.historical_datas[symbol] is None:
            self.historical_datas[symbol] = self.clientMongos[symbol].find()
        return self.historical_datas[symbol]

    async def get_historical_dataframe_updated(self, symbol ):
        data = pd.DataFrame( await self.get_historical_datas_updated( symbol ) )
        data.set_index('Date', inplace = True)
        return data

    async def fetch_and_store_max_history_loop(self ):
        while True:
            await asyncio.sleep(60)
            self.fetch_and_store_max_history()

    async def fetch_and_store_max_history(self ):
        for symbol in self.symbols:
            log.info( "[HISTORY] : Fetch history for symbol %s",self.symbol)
            last_data = self.clientMongo.last()
            all_datas = []
            for provider in self.providers:
                datas = await provider.fetch_max_history( symbol, last_data )
                all_datas += datas
            self.clientMongos[symbol].insert_multiple( all_datas )
            self.historical_datas[symbol] += all_datas

    async def plot_history(self, symbol, label='Open' ):
        datas = await self.get_historical_datas_updated( symbol )
        history = pd.DataFrame(datas)
        history.set_index('Date', inplace = True)
        history.plot(y=label)
        plt.show()

    async def fetch_time_delta_history(self, symbol, minutes_number):
        for provider in self.providers:
            return await provider.fetch_time_delta_history( symbol, minutes_number )



