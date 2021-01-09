from datetime import datetime

import pandas as pd
import yfinance as yf

from analyzer.mongodb_client_history import MongoDbClientHistory


class YahooHistoricProvider():

    # def __init__(self):

    async def send_max_history( self, symbol):

        data1 = yf.download( tickers = symbol,period = "6d",interval = "1m",group_by = 'ticker',auto_adjust = True,prepost = True,threads = True,proxy = None)
        data2 = yf.download( tickers = symbol,period = "max",interval = "30m",group_by = 'ticker',auto_adjust = True,prepost = True,threads = True,proxy = None)
        data3 = yf.download( tickers = symbol,period = "max",interval = "1d",group_by = 'ticker',auto_adjust = True,prepost = True,threads = True,proxy = None)

        data=pd.concat( [data1, data2, data3], ignore_index=False)
        data['datetime'] = data.index
        data['timestamp'] = data['datetime'].apply(lambda dt: datetime.timestamp(dt))

        data.drop_duplicates(subset=['timestamp'])

        client = MongoDbClientHistory( symbol )
        all_datas = []
        for index, row in data.iterrows():
            cleanData = {
                "ctm" : int(row['timestamp'])*1000,
                "open" : row['Open'],
                "close" : row['Close'],
                "high" : row['High'],
                "low" : row['Low'],
                "vol" : row['Volume']
            }
            all_datas.append(cleanData)
        client.insert_multiple( all_datas )

