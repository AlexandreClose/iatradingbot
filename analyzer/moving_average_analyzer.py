import pandas as pd

from dao.mongodb_client_history import MongoDbClientHistory


class MovingAverageAnalyzer:

    def __init__(self, symbol):
        self.symbol = symbol
        self.datas = self._get_history_dataframe( symbol )


    def _get_history_dataframe(self, symbol ):
        client = MongoDbClientHistory( symbol )
        datas = list(client.find())
        datas = pd.DataFrame.from_records(datas)

        return datas

    def get_datas(self):
        return self.datas

    def compute_average_rolling(self, window_size):
        avg_rolling = self.datas.rolling(window=window_size).mean()
        return avg_rolling
