import asyncio
import concurrent

import pandas as pd
import schedule
import matplotlib.pyplot as plt
import time
from logging_conf import log

from dao.mongodb_client_history import MongoDbClientHistory

class HistoricManager():
    def __init__(self, loop, symbol,*providers):
        self.datas = []
        self.clientMongo = MongoDbClientHistory( symbol )
        self.providers=providers
        self.symbol = symbol
        loop.run_until_complete( self.fetch_and_store_max_history( ) )
        loop.create_task(self.fetch_and_store_max_history())


    async def get_historical_datas_updated(self):
        return self.clientMongo.find()

    async def get_historical_dataframe_updated(self):
        data = pd.DataFrame( await self.get_historical_datas_updated() )
        data.set_index('Date', inplace = True)
        return data

    async def fetch_and_store_max_history_loop(self ):
        while True:
            await asyncio.sleep(60)
            self.fetch_and_store_max_history()

    async def fetch_and_store_max_history(self ):
        log.info( "[HISTORY] : Fetch history for symbol %s",self.symbol)
        last_data = self.clientMongo.last()
        all_datas = []
        for provider in self.providers:
            provider.set_symbol( self.symbol)
            datas = await provider.fetch_max_history(last_data)
            all_datas += datas
        self.clientMongo.insert_multiple( all_datas )

    async def plot_history(self, label='Open' ):
        datas = await self.get_historical_datas_updated()
        history = pd.DataFrame(datas)
        history.set_index('Date', inplace = True)
        history.plot(y=label)
        plt.show()

    async def fetch_time_delta_history(self, minutes_number):
        for provider in self.providers:
            return await provider.fetch_time_delta_history( minutes_number )



