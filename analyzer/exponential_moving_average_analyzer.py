import numpy as np
import pandas as pd

from dao.mongodb_client_history import MongoDbClientHistory
from historicprovider.historic_manager import HistoricManager


class ExponentialMovingAverageAnalyzer:

    async def compute_exponential_moving_average(self, symbol, window_size):
        dataframe = await HistoricManager.instance().get_historical_dataframe_updated( symbol )
        print(dataframe)
        ema = dataframe.ewm(span=window_size, adjust=False).mean()
        print(ema)
        dataframe['ema_Open']=ema['Open']
        dataframe['ema_Close']=ema['Close']
        dataframe['ema_High']=ema['High']
        dataframe['ema_Low']=ema['Low']
        dataframe['ema_Volume']=ema['Volume']
        return dataframe

    async def search_zeros_with_historic(self, symbol, window_size):
        df = await self.compute_exponential_moving_average( symbol, window_size)
        df['difference']=df['Open']-df['ema_Open']
        df['cross_sign'] = np.sign(df.difference.shift(1)) - np.sign(df.difference)
        df['cross'] = np.sign(df.difference.shift(1)) != np.sign(df.difference)
        np.sum(df.cross)-1
        print ( df['cross'])
        print ( df['cross_sign'])


