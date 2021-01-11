import pandas as pd

from dao.mongodb_client_history import MongoDbClientHistory


class ExponentialMovingAverageAnalyzer:

    def __init__(self, symbol ):
        self.symbol = symbol
        self.datas = self._get_history_dataframe( symbol )


    def _get_history_dataframe(self, symbol ):
        client = MongoDbClientHistory( symbol )
        datas = list(client.find())
        datas = pd.DataFrame.from_records(datas)

        return datas

    def get_datas(self):
        return self.datas

    def compute_exponential_moving_average(self, window_size):
        ema = self.datas.ewm(span=window_size, adjust=False).mean()
        return [ema, self.datas]
