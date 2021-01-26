import asyncio

import pandas as pd
import matplotlib.pyplot as plt

from historicprovider.xtb_historic_provider import  xtb_historic_provider
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
        self.providers=[ xtb_historic_provider ]
        self.historical_datas ={}

    async def register_provider(self, provider ):
        self.providers.append(provider)

    async def register_symbol(self, symbol ):
        if not self.symbols:
            asyncio.create_task(self.fetch_and_store_max_history_loop( ))

        if symbol not in self.symbols:
            self.symbols.append( symbol )
            self.clientMongos[symbol]=MongoDbClientHistory( symbol )
            self.historical_datas[symbol]=[]

    async def unregister_symbol(self, symbol ):
        if symbol in self.symbols: self.symbols.remove( symbol )
        if symbol in self.clientMongos: del self.clientMongos[ symbol ]
        if symbol in self.historical_datas: del self.historical_datas[ symbol ]


    async def get_historical_datas_updated(self, symbol ):
        if not self.historical_datas[symbol]:
            self.historical_datas[symbol] = self.clientMongos[symbol].find()
        return self.historical_datas[symbol]

    async def get_historical_dataframe_updated(self, symbol ):
        datas = await self.get_historical_datas_updated( symbol )
        df = pd.DataFrame( datas )
        df['Date'] = pd.to_datetime(df['Date'],unit='s')
        df.set_index('Date', inplace = True)
        df = df.sort_index()
        return df

    async def fetch_and_store_max_history_loop(self ):
        await asyncio.sleep(1)
        while True:
            await self.fetch_and_store_max_history()
            await asyncio.sleep(60)

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

historic_manager = HistoricManager.instance()
