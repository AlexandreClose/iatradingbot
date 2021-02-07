import asyncio

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from historicprovider.xtb_historic_provider import  xtb_historic_provider
from logging_conf import log

from dao.dao_history import MongoDbClientHistory
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
            datas_from_mongo = []
            while len(datas_from_mongo) == 0:
                datas_from_mongo = self.clientMongos[symbol].find()
                await asyncio.sleep(1)
            self.historical_datas[symbol] = datas_from_mongo
        return self.historical_datas[symbol]

    async def get_historical_dataframe_updated(self, symbol, lastDays=None ):
        datas = await self.get_historical_datas_updated( symbol )

        if datas:
            df = pd.DataFrame( datas )
            df['Date'] = pd.to_datetime(df['Date'],unit='s')
            df.set_index('Date', inplace = True)
            df = df.sort_index()
            if lastDays is not None:
                today = datetime.today().date()
                df = df[today - pd.offsets.Day(lastDays):]
            return df
        return None

    async def fetch_and_store_max_history_loop(self ):
        while True:
            await asyncio.sleep(60)
            await self.fetch_and_store_max_history()


    async def fetch_and_store_max_history(self ):
        for symbol in self.symbols:
            log.info( "[HISTORY] : Fetch history delta for symbol %s",symbol)
            last_data = self.clientMongos[symbol].last()
            all_datas = []
            for provider in self.providers:
                datas = await provider.fetch_max_history( symbol, last_data )
                all_datas += datas
            self.clientMongos[symbol].insert_multiple( all_datas )
            self.historical_datas[symbol] += all_datas

    async def plot_history(self, symbol, label='Open' ):
        history= await self.get_historical_dataframe_updated( symbol )
        log.info( '[PLOT] : plot history of symbol %s with following datas', symbol)
        history.plot(y=label)
        plt.show()

    async def fetch_time_delta_history(self, symbol, minutes_number):
        datas = []
        for provider in self.providers:
            datas += await provider.fetch_time_delta_history( symbol, minutes_number )
        return datas

historic_manager = HistoricManager.instance()
