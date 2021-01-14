import pandas as pd

from dao.mongodb_client_history import MongoDbClientHistory


class MovingAverageAnalyzer:

    def __init__(self, history_manager ):
        self.history_manager = history_manager

    async def compute_moving_average(self, window_size):
        dataframe = await self.history_manager.get_historical_dataframe_updated()
        avg_rolling = dataframe.rolling(window=window_size).mean()
        return avg_rolling,dataframe
