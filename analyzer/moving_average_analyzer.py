import datetime

import numpy as np
import pandas as pd
from datetime import date

from dao.mongodb_client_history import MongoDbClientHistory
from historicprovider.historic_manager import HistoricManager
from logging_conf import log



class MovingAverageAnalyzer:

    def __init__(self, symbol, type = 'lma', small_windows_size = 3, long_windows_size = 100, optimize_sws_lws = False, enveloppe=0 ):
        self.symbol = symbol
        self.type = type
        self.small_windows_size=small_windows_size
        self.long_windows_size = long_windows_size
        self.enveloppe=enveloppe
        if optimize_sws_lws:
            (sws_max_profit, lws_max_profit, max_profit ) = self.optimize_windows_size( symbol )
            self.small_windows_size = sws_max_profit
            self.long_windows_size = lws_max_profit
        self.commission = 1


    async def compute_exponential_moving_average(self):
        dataframe = await HistoricManager.instance().get_historical_dataframe_updated( self.symbol )
        dataframe=dataframe.resample("1D").bfill()

        if self.type == 'lma':
            lma = dataframe.ewm(span=self.long_windows_size, adjust=False).mean()
        elif self.type == 'ma':
            lma = dataframe.rolling(window=self.long_windows_size).mean()
        else:
            lma = dataframe.ewm(span=self.long_windows_size, adjust=False).mean()
        dataframe['lma_Open']=lma['Open']
        dataframe['lma_Close']=lma['Close']
        dataframe['lma_High']=lma['High']
        dataframe['lma_Low']=lma['Low']
        dataframe['lma_Volume']=lma['Volume']
        
        if self.enveloppe > 0:
            dataframe['lma_top_Open']=dataframe['lma_Open']+self.enveloppe*0.01*dataframe['lma_Open']
            dataframe['lma_top_Close']=dataframe['lma_Close']+self.enveloppe*0.01*dataframe['lma_Close']
            dataframe['lma_top_High']=dataframe['lma_High']+self.enveloppe*0.01*dataframe['lma_High']
            dataframe['lma_top_Low']=dataframe['lma_Low']+self.enveloppe*0.01*dataframe['lma_Low']
            dataframe['lma_top_Volume']=dataframe['lma_Volume']+self.enveloppe*0.01*dataframe['lma_Volume']

            dataframe['lma_bottom_Open']=dataframe['lma_Open']-self.enveloppe*0.01*dataframe['lma_Open']
            dataframe['lma_bottom_Close']=dataframe['lma_Close']-self.enveloppe*0.01*dataframe['lma_Close']
            dataframe['lma_bottom_High']=dataframe['lma_High']-self.enveloppe*0.01*dataframe['lma_High']
            dataframe['lma_bottom_Low']=dataframe['lma_Low']-self.enveloppe*0.01*dataframe['lma_Low']
            dataframe['lma_bottom_Volume']=dataframe['lma_Volume']-self.enveloppe*0.01*dataframe['lma_Volume']



        sma = dataframe.ewm(span=self.small_windows_size, adjust=False).mean()
        dataframe['sma_Open']=sma['Open']
        dataframe['sma_Close']=sma['Close']
        dataframe['sma_High']=sma['High']
        dataframe['sma_Low']=sma['Low']
        dataframe['sma_Volume']=sma['Volume']

        sma_slope = pd.Series(np.gradient(dataframe['sma_Close']), dataframe.index, name='sma_slope')
        dataframe = pd.concat([dataframe, sma_slope], axis=1)
        dataframe['sma_slope']=dataframe['sma_slope']/dataframe['sma_Open']*100


        dataframe.interpolate()

        return dataframe

    async def compute_trading_signal_now(self):
        ldf = await self.compute_trading_signals( )
        if not ldf.empty:
            today = date.today()
            d1 = today.strftime("%Y-%m-%d")
            last_signal = ldf.loc[ldf.index == d1]
            if not last_signal.empty:
                signal = last_signal.to_dict(orient='records')[0]
                signal_timestamp = datetime.datetime.now().timestamp()
                signal_datetime = datetime.datetime.now()
                signal_type = "BUY" if signal['cross_sma_Close_lma_top_Close'] else "SELL"
                signal = {
                    "type" : signal_type,
                    "Timestamp":signal_timestamp,
                    "Date":d1,
                    "DateTime":signal_datetime.isoformat(),
                    "DateString":signal['DateString'],
                    "Open":signal['Open'],
                    "Close":signal['Close'],
                    "High":signal['High'],
                    "Low":signal['Low'],
                    "Volume":signal['Volume'],
                    "infos":signal
                }
                return signal
        return None


    async def compute_trading_signals( self ):
        df = await self.compute_exponential_moving_average( )

        if self.enveloppe == 0:
            df['diff_sma_Close_lma_Close']=df['sma_Close']-df['lma_Close']
            df['cross_sign_sma_Close_lma_Close'] = np.sign(df['diff_sma_Close_lma_Close'].shift(-1) * np.sign(df['diff_sma_Close_lma_Close']))*np.sign(df['diff_sma_Close_lma_Close'])
            df['cross_sma_Close_lma_Close'] = - np.sign(df['diff_sma_Close_lma_Close'].shift(-1)) != np.sign(df['diff_sma_Close_lma_Close'])
            df = df[(df['cross_sma_Close_lma_Close']==True)]
        else :
            df['diff_sma_Close_lma_Close']=df['sma_Close']-df['lma_Close']

            df_top = df
            df_top['diff_sma_Close_lma_top_Close']=df_top['sma_Close']-df_top['lma_top_Close']
            df_top['cross_sign_sma_Close_lma_Close'] = np.sign(df_top['diff_sma_Close_lma_top_Close'].shift(-1) * np.sign(df_top['diff_sma_Close_lma_top_Close']))*np.sign(df_top['diff_sma_Close_lma_top_Close'])
            df_top['cross_sma_Close_lma_top_Close'] =  np.sign(df_top['diff_sma_Close_lma_top_Close'].shift(-1)) != np.sign(df_top['diff_sma_Close_lma_top_Close'])
            df_top = df_top[(df_top['cross_sma_Close_lma_top_Close']==True) ]
            df_top = df_top[(df_top['cross_sign_sma_Close_lma_Close']>0)]

            df_bottom = df
            df_bottom['diff_sma_Close_lma_bottom_Close']=df_bottom['sma_Close']-df_bottom['lma_bottom_Close']
            df_bottom['cross_sign_sma_Close_lma_Close'] = np.sign(df_bottom['diff_sma_Close_lma_bottom_Close'].shift(-1) * np.sign(df_bottom['diff_sma_Close_lma_bottom_Close']))*np.sign(df_bottom['diff_sma_Close_lma_bottom_Close'])
            df_bottom['cross_sma_Close_lma_bottom_Close'] = np.sign(df_bottom['diff_sma_Close_lma_bottom_Close'].shift(-1)) != np.sign(df_bottom['diff_sma_Close_lma_bottom_Close'])
            df_bottom = df_bottom[(df_bottom['cross_sma_Close_lma_bottom_Close']==True) ]
            df_bottom = df_bottom[(df_bottom['cross_sign_sma_Close_lma_Close']<0)]
            
            df = pd.concat( [ df_top,df_bottom])

            df=df.sort_index()

        # filter on derivative
        df=df[df['cross_sign_sma_Close_lma_Close']!=df.shift(-1)['cross_sign_sma_Close_lma_Close']]

        df=df[(df['sma_slope'].abs() >1.2)]
        df=df[df['cross_sign_sma_Close_lma_Close']!=df.shift(-1)['cross_sign_sma_Close_lma_Close']]

        return df

    async def compute_profit(self):
        df_signals = await self.compute_trading_signals( )
        df_signals['profit'] = (df_signals['Close'].shift(-1)-df_signals['Close'])* df_signals['cross_sign_sma_Close_lma_Close'] - self.commission * 0.01*df_signals['Close'].shift(-1)
        sum_profit = df_signals['profit'].sum()
        return (df_signals,sum_profit)

    async def optimize (self ):
        sws_max_profit = None
        lws_max_profit = None
        enveloppe_max_profit = None
        max_profit = None
        trading_signals_max_profit = None
        for sws in range( 1,4 ):
            log.info( '[EMA] Optimization iter with sws : %s', sws)
            for lws in range ( 80, 120 ):
                for enveloppe in range( 1, 2 ):
                    self.enveloppe = enveloppe
                    self.small_windows_size = sws
                    self.long_windows_size = lws
                    (df_signals,profit) = await self.compute_profit( )
                    if max_profit == None or profit > max_profit :
                        max_profit = profit
                        sws_max_profit = sws
                        lws_max_profit = lws
                        enveloppe_max_profit = enveloppe
                        trading_signals_max_profit = df_signals
        log.info( "[EMA] Optimize for %s", self.symbol )
        log.info( "[EMA] Small windows size : %s", sws_max_profit )
        log.info( "[EMA] Long windows size : %s", lws_max_profit )
        log.info( "[EMA] Enveloppe : %s", enveloppe_max_profit )
        log.info( "[EMA] Max profit : %s", max_profit )
        log.info( "[EMA] Trading positions number : %s", len(trading_signals_max_profit) )
        return (trading_signals_max_profit,sws_max_profit, lws_max_profit, enveloppe, max_profit )








