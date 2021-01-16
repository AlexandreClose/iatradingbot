import pandas as pd

from dao.mongodb_client_history import MongoDbClientHistory
from historicprovider.historic_manager import HistoricManager


class MovingAverageAnalyzer:

    async def compute_moving_average(self, symbol, window_size):
        dataframe = await HistoricManager.instance().get_historical_dataframe_updated( symbol )
        avg_rolling = dataframe.rolling(window=window_size).mean()
        dataframe['ma_Open']=avg_rolling['Open']
        dataframe['ma_Close']=avg_rolling['Close']
        dataframe['ma_High']=avg_rolling['High']
        dataframe['ma_Low']=avg_rolling['Low']
        dataframe['ma_Volume']=avg_rolling['Volume']
        return dataframe
