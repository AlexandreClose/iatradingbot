import pandas as pd

from dao.mongodb_client_history import MongoDbClientHistory


class ExponentialMovingAverageAnalyzer:

    def __init__(self, history_manager ):
        self.history_manager = history_manager

    async def compute_exponential_moving_average(self, window_size):
        dataframe = await self.history_manager.get_historical_dataframe_updated()
        ema = dataframe.ewm(span=window_size, adjust=False).mean()
        return ema,dataframe
