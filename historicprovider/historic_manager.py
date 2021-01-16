import asyncio

import pandas as pd
import matplotlib.pyplot as plt
from logging_conf import log

from dao.mongodb_client_history import MongoDbClientHistory
from utils.singleton import Singleton

def extract_time(json):
    try:
        return int(json['Date'])
    except KeyError:
        return 0

@Singleton
class HistoricManager( ):

    def __init__(self ):
        self.datas = []
        self.symbols = []
        self.clientMongos = { }
        self.providers=[]
        self.historical_datas ={}

    async def register_provider(self, provider ):
        self.providers.append(provider)

    async def register_symbol(self, symbol ):
        self.symbols.append( symbol )
        self.clientMongos[symbol]=MongoDbClientHistory( symbol )
        await self.fetch_and_store_max_history( )
        asyncio.create_task(self.fetch_and_store_max_history_loop( ))
        self.historical_datas[symbol]=[]

    async def get_historical_datas_updated(self, symbol ):
        if not self.historical_datas[symbol]:
            self.historical_datas[symbol] = self.clientMongos[symbol].find()
        return self.historical_datas[symbol]

    async def get_historical_dataframe_updated(self, symbol ):
        datas = await self.get_historical_datas_updated( symbol )
        dataframe = pd.DataFrame( datas )
        dataframe['Date'] = pd.to_datetime(dataframe['Date'],unit='s')
        dataframe.set_index('Date', inplace = True)
        dataframe = dataframe.sort_index()
        return dataframe

    async def fetch_and_store_max_history_loop(self ):
        while True:
            await asyncio.sleep(60)
            await self.fetch_and_store_max_history() # this allow to fetch only last minute of history, recursively

    async def fetch_and_store_max_history(self ):
        for symbol in self.symbols:
            if symbol not in self.historical_datas:
                self.historical_datas[symbol] = []
            log.info( "[HISTORY] : Fetch history for symbol %s",symbol)
            last_data = self.clientMongos[symbol].last()
            all_datas = []
            for provider in self.providers:
                datas = await provider.fetch_max_history( symbol, last_data )
                all_datas += datas
            self.clientMongos[symbol].insert_multiple( all_datas )
            self.historical_datas[symbol].append( all_datas )

    async def plot_history(self, symbol, label='Open' ):
        history= await self.get_historical_dataframe_updated( symbol )
        log.info( '[PLOT] : plot history of symbol %s with following datas', symbol)
        print ( history )
        history.plot(y=label)
        plt.show()

    async def fetch_time_delta_history(self, symbol, minutes_number):
        datas = []
        for provider in self.providers:
            datas += await provider.fetch_time_delta_history( symbol, minutes_number )
        return datas


