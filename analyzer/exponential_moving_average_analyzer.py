import numpy as np
import pandas as pd

from dao.mongodb_client_history import MongoDbClientHistory
from historicprovider.historic_manager import HistoricManager


class ExponentialMovingAverageAnalyzer:

    async def compute_exponential_moving_average(self, symbol, small_windows_size, window_size):
        dataframe = await HistoricManager.instance().get_historical_dataframe_updated( symbol )
        dataframe=dataframe.resample("1D").mean()
        ema = dataframe.ewm(span=window_size, adjust=False).mean()
        sma = dataframe.rolling(window=small_windows_size).mean()
        dataframe['ema_Open']=ema['Open']
        dataframe['ema_Close']=ema['Close']
        dataframe['ema_High']=ema['High']
        dataframe['ema_Low']=ema['Low']
        dataframe['ema_Volume']=ema['Volume']
        dataframe['sma_Open']=sma['Open']
        dataframe['sma_Close']=sma['Close']
        dataframe['sma_High']=sma['High']
        dataframe['sma_Low']=sma['Low']
        dataframe['sma_Volume']=sma['Volume']

        return dataframe

    async def search_zeros_with_historic(self, symbol, window_size):
        df = await self.compute_exponential_moving_average( symbol, window_size)
        df['difference']=df['Open']-df['ema_Open']
        df['cross_sign'] = np.sign(df.difference.shift(1) - np.sign(df.difference))
        df['cross'] = np.sign(df.difference.shift(1)) != np.sign(df.difference)
        df_zeros = df[(df['cross']==True)]
        df_zeros=df_zeros.dropna()
        return df_zeros

    async def compute_trading_signals(self,symbol, window_size):
        df_signals = await self.search_zeros_with_historic( symbol, window_size )
        print( df_signals)
        df_signals['profit'] = (df_signals['Open'].shift(-1)-df_signals['Open'])*( - df_signals['cross_sign'])
        df_signals=df_signals.dropna()
        print ( df_signals.head(100 ) )
        sum_profit = df_signals['profit'].sum()
        print( sum_profit )





