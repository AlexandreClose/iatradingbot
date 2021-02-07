import datetime
import json

import numpy as np
import pandas as pd
from datetime import date

from manager.historic_manager import HistoricManager
from logging_conf import log
import matplotlib.pyplot as plt



class MovingAverageAnalyzer:

    def __init__(self, symbol, type = 'lma', small_windows_size = 3, long_windows_size = 100, enveloppe=1.0, derivative_abs_limit = 0.0, time_type="daily" ):
        self.symbol = symbol
        self.type = type
        self.small_windows_size=small_windows_size
        self.long_windows_size = long_windows_size
        self.enveloppe=enveloppe
        self.commission = 1
        self.time_type = time_type
        self.derivative_abs_limit = derivative_abs_limit


    async def compute_exponential_moving_average(self ):
        if self.time_type == 'daily':
            dataframe = await HistoricManager.instance().get_historical_dataframe_updated( self.symbol )
            dataframe=dataframe.resample("1D").bfill()

        if self.time_type == 'intraday':
            dataframe = await HistoricManager.instance().get_historical_dataframe_updated( self.symbol, lastDays=29 )
            dataframe=dataframe.resample("1Min").bfill()

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
        # trading_positions,ldf = await self.compute_trading_signals( )
        ldf,trading_positions = await self.compute_trading_signals( )
        if not ldf.empty:
            today = date.today()
            d1 = today.strftime("%Y-%m-%d")
            last_signal = ldf.loc[ldf.index == d1]
            if not last_signal.empty:
                signal = last_signal.to_dict(orient='records')[0]
                print( signal )
                signal_timestamp = datetime.datetime.now().timestamp()
                signal_datetime = datetime.datetime.now()
                signal_type = "BUY" if signal['cross_sma_Close_lma_Close'] else "SELL"
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
            df['cross_sma_Close_lma_Close'] = np.sign(df['diff_sma_Close_lma_Close'].shift(-1)) != np.sign(df['diff_sma_Close_lma_Close'])
            trading_positions = df[(df['cross_sma_Close_lma_Close']==True)]
            trading_positions=trading_positions.sort_index()
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

            trading_positions = pd.concat( [ df_top,df_bottom])

            trading_positions=trading_positions.sort_index()

        # filter some trading positions
        trading_positions=trading_positions[trading_positions['cross_sign_sma_Close_lma_Close']!=trading_positions.shift(-1)['cross_sign_sma_Close_lma_Close']]

        trading_positions=trading_positions[(trading_positions['sma_slope'].abs() >=self.derivative_abs_limit)]
        trading_positions=trading_positions[trading_positions['cross_sign_sma_Close_lma_Close']!=trading_positions.shift(-1)['cross_sign_sma_Close_lma_Close']]
        trading_positions = trading_positions[(trading_positions['cross_sign_sma_Close_lma_Close'] > 0).idxmax():]


        trading_positions_sign = trading_positions['cross_sign_sma_Close_lma_Close']

        # Fill original dataframe with trading position

        if self.time_type == 'daily':
            trading_positions_sign=trading_positions_sign.resample("1D").ffill()

        if self.time_type == 'intraday':
            trading_positions_sign=trading_positions_sign.resample("1Min").ffill()

        df['trading_positions'] = trading_positions_sign
        df['trading_positions'] = df['trading_positions'].fillna(0)

        return trading_positions, df

    async def compute_profit(self):
        df_signals, df = await self.compute_trading_signals( )
        df['log_return'] = np.log(df['Close']).diff()
        df['log_return'] = df['log_return']*df['trading_positions']
        df['cumsum_log_return'] = df['log_return'].cumsum()
        df['cumsum_relative_log_return'] = np.exp(df['cumsum_log_return']) - 1
        return df,df['cumsum_relative_log_return'][-1],df_signals

    async def optimize (self, params_opti = None ):
        return_params_opti = {}
        if not params_opti :
            if self.time_type == 'daily':
                range_sws = range( 1,2 );
                range_lws = range ( 95, 105 )
                range_enveloppe = np.linspace(0,3,3)
                range_derivative_abs_limit = np.linspace(0,0.1,3)

            if self.time_type == 'intraday':
                range_sws = range( 1,2 );
                range_lws = range ( 15, 25 )
                range_enveloppe = np.linspace(0,3,3)
                range_derivative_abs_limit = np.linspace(0,0.1,3)


            list_tested_values = []
            log.info( '[EMA] Process optimisation for symbol %s', self.symbol)
            for sws in range_sws:
                for lws in range_lws:
                    for enveloppe in range_enveloppe:
                        for derivative_abs_limit in range_derivative_abs_limit:
                            try:
                                self.small_windows_size = sws
                                self.long_windows_size = lws
                                self.enveloppe = enveloppe
                                self.derivative_abs_limit = derivative_abs_limit
                                (df_profit,profit,trading_signals) = await self.compute_profit( )
                                list_tested_values.append( {
                                    "enveloppe":enveloppe,
                                    "sws":sws,
                                    "lws":lws,
                                    "derivative_abs_limit":derivative_abs_limit,
                                    "nb_trades":len(trading_signals),
                                    "profit":profit
                                })
                            except Exception as e:
                                log.error( e )

            # Make a panda DF with all the combinations
            df_best_values = pd.DataFrame( list_tested_values)
            df_best_values=df_best_values.sort_values(by=['profit','nb_trades'], ascending=[False,False])

            best_values = df_best_values.head(1).to_dict('records')[0]
            sws_opti=best_values['sws']
            lws_opti=best_values['lws']
            enveloppe_opti=best_values['enveloppe']
            derivative_opti=best_values['derivative_abs_limit']
            trading_signals_number_opti=best_values['nb_trades']
            profit_opti=best_values['profit']
            log.info( "[EMA] Optimize for %s", self.symbol )
            log.info( "[EMA] Small windows size : %s", sws_opti )
            log.info( "[EMA] Long windows size : %s", lws_opti )
            log.info( "[EMA] Enveloppe : %s", enveloppe_opti )
            log.info( "[EMA] Derivative : %s", derivative_opti )
            log.info( "[EMA] Max profit : %s", profit_opti )
            log.info( "[EMA] Trading positions number : %s", trading_signals_number_opti )
            self.small_windows_size = sws_opti
            self.long_windows_size = lws_opti
            self.enveloppe = enveloppe_opti
            self.derivative_abs_limit = derivative_opti
            return_params_opti = {
                "sws":sws_opti,
                "lws":lws_opti,
                "enveloppe":enveloppe_opti,
                "derivative_abs_limit":derivative_abs_limit,
                "profit":profit_opti,
                "trading_signals_number":trading_signals_number_opti
            }
        else:
            log.info( "Optimized params given for symbol %s. No need to process optimization", self.symbol)
            log.info( "[EMA] Optimize for %s", self.symbol )
            log.info( "[EMA] Small windows size : %s", params_opti["sws"] )
            log.info( "[EMA] Long windows size : %s", params_opti["lws"] )
            log.info( "[EMA] Enveloppe : %s", params_opti["enveloppe"] )
            log.info( "[EMA] Derivative : %s", params_opti["derivative_abs_limit"] )
            log.info( "[EMA] Max profit : %s", params_opti["profit"] )
            log.info( "[EMA] Trading positions number : %s", params_opti["trading_signals_number"] )
            self.small_windows_size = params_opti["sws"]
            self.long_windows_size = params_opti["lws"]
            self.enveloppe = params_opti["enveloppe"]
            self.derivative_abs_limit = params_opti["derivative_abs_limit"]
            return_params_opti = params_opti

        return return_params_opti








