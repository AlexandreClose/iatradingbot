from datetime import datetime

import pandas as pd
import yfinance as yf

from dao.mongodb_client_history import MongoDbClientHistory
from utils.singleton import Singleton


def extract_time(json):
    try:
        return int(json['Date'])
    except KeyError:
        return 0

@Singleton
class YahooHistoricProvider():

    async def fetch_max_history(self, symbol, last_data = None ):

        if symbol == 'BITCOIN':
            symbol = 'BTC-USD'

        ticker = yf.Ticker(symbol)
        data1 = ticker.history(period="100y",interval="1d")
        data2 = ticker.history(period="7d",interval="1m")
        data=pd.concat( [data1,data2], ignore_index=False)

        data['datetime'] = data.index
        data['timestamp'] = data['datetime'].apply(lambda dt: datetime.timestamp(dt))

        data.drop_duplicates(subset=['timestamp'])

        all_datas = []
        for index, row in data.iterrows():
            cleanData = {
                "Date" : int(row['timestamp']),
                "Open" : row['Open'],
                "Close" : row['Close'],
                "High" : row['High'],
                "Low" : row['Low'],
                "Volume" : row['Volume']
            }
            all_datas.append(cleanData)
        all_datas.sort(key=extract_time)
        return all_datas

    async def fetch_time_delta_history(self, symbol, minutes_number):
        if symbol == 'BITCOIN':
            symbol = 'BTC-USD'

        ticker = yf.Ticker(symbol)
        data1 = ticker.history(period="1d",interval="1m")
        data=pd.concat( [data1], ignore_index=False)

        data['datetime'] = data.index
        data['timestamp'] = data['datetime'].apply(lambda dt: datetime.timestamp(dt))

        timestamp_now = datetime.now()
        timestart_n_minutes_earlier = timestamp_now - datetime.timedelta(minutes=minutes_number).total_seconds()
        data=data[(data['timestamp'] > timestart_n_minutes_earlier )]

        data.drop_duplicates(subset=['timestamp'])
        all_datas = []
        for index, row in data.iterrows():
            cleanData = {
                "Date" : int(row['timestamp']),
                "Open" : row['Open'],
                "Close" : row['Close'],
                "High" : row['High'],
                "Low" : row['Low'],
                "Volume" : row['Volume']
            }
            all_datas.append(cleanData)
        all_datas.sort(key=extract_time)

        return all_datas

yahoo_historic_provider=YahooHistoricProvider.instance()
