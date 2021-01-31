import asyncio
import unittest

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analyzer.moving_average_analyzer import MovingAverageAnalyzer
from manager.historic_manager import historic_manager
from logging_conf import log
from trading_client.trading_client import trading_client
import matplotlib.dates as mdates


def onresize( event ):
    plt.tight_layout()


class TestMovingAverageAnalyzer(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestMovingAverageAnalyzer, self).__init__(*args, **kwargs)
        self.symbol = 'MSFT.US_9'
        self.movingAverageAnalyzer= MovingAverageAnalyzer( self.symbol, 'ema', 3, 20 ,1.0, 0.01)
        loop = asyncio.get_event_loop()
        loop.run_until_complete( trading_client.login("11769869","TestTest123123", False))
        loop.run_until_complete( historic_manager.register_symbol( self.symbol))

    def test_plot_history_dataframe(self):
        loop = asyncio.get_event_loop()
        ema=loop.run_until_complete( self.movingAverageAnalyzer.compute_exponential_moving_average( ) )
        ax = ema.plot(y= 'lma_Close', color="C1")
        ema.plot(y='sma_Close', color='C2', ax = ax)
        plt.show()

    def test_compute_exponential_moving_average_last(self):
        loop = asyncio.get_event_loop()
        df=loop.run_until_complete( self.movingAverageAnalyzer.compute_exponential_moving_average( ) )
        log.info( '[EMA] : Last computation')
        print ( df )
        log.info( '[EMA] : Size last computation : %s', len(df))

    def test_compute_trading_signal_now(self):
        loop = asyncio.get_event_loop()
        df=loop.run_until_complete( self.movingAverageAnalyzer.compute_trading_signal_now( ) )

    def test_compute_trading_signal(self):
        loop = asyncio.get_event_loop()
        df=loop.run_until_complete( self.movingAverageAnalyzer.compute_trading_signals() )
        log.info( '[TRADING POSITIONS] : %s positions taken', len(df))
        print(df)

    def test_plot_trading_positions(self):
        loop = asyncio.get_event_loop()
        ema=loop.run_until_complete( self.movingAverageAnalyzer.compute_exponential_moving_average( ) )
        trading_positions,df=loop.run_until_complete( self.movingAverageAnalyzer.compute_trading_signals() )
        log.info( '[TRADING POSITIONS] : %s positions taken', len(trading_positions))

        ax=ema.plot(y='Close', color='C1')
        trading_positions['color_trading']=np.where(trading_positions['cross_sign_sma_Close_lma_Close']>0, 'green', 'red')
        plt.scatter(trading_positions.index, trading_positions['sma_Close'],c=trading_positions['color_trading'])
        # ax.set_xlim(pd.Timestamp('2016-01-01'), pd.Timestamp('2017-01-01'))
        plt.tight_layout()
        plt.gcf().canvas.mpl_connect('resize_event', onresize)
        plt.show( )

    def test_plot_trading_positions_doc(self):
        start_date = '2015-01-01'
        end_date = '2016-12-31'
        my_year_month_fmt = mdates.DateFormatter('%m/%y')
        loop = asyncio.get_event_loop()
        ema=loop.run_until_complete( self.movingAverageAnalyzer.compute_exponential_moving_average( ) )
        trading_positions,df=loop.run_until_complete( self.movingAverageAnalyzer.compute_trading_signals() )
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16,9))

        ax1.plot(ema.loc[start_date:end_date, :].index, ema.loc[start_date:end_date, 'Close'], label = 'EMA')

        ax1.set_ylabel('$')
        ax1.legend(loc='best')
        # ax1.xaxis.set_major_formatter(my_year_month_fmt)

        ax2.plot(df.loc[start_date:end_date, :].index, df.loc[start_date:end_date, 'trading_positions'],
                 label='Trading position')

        ax2.set_ylabel('Trading position')
        ax2.xaxis.set_major_formatter(my_year_month_fmt)
        plt.show()


    def test_compute_profit(self ):
        loop = asyncio.get_event_loop()
        df_trading,df = loop.run_until_complete( self.movingAverageAnalyzer.compute_profit())

    def test_compute_profit_doc(self ):
        my_year_month_fmt = mdates.DateFormatter('%m/%y')

        loop = asyncio.get_event_loop()
        df_profit,profit,trading_signals = loop.run_until_complete( self.movingAverageAnalyzer.compute_profit())
        cum_strategy_asset_relative_returns=df_profit['cumsum_relative_log_return']
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16,9))

        ax1.plot(df_profit.index, cum_strategy_asset_relative_returns, label='MSFT')

        ax1.set_ylabel('Cumulative log-returns')
        ax1.legend(loc='best')
        ax1.xaxis.set_major_formatter(my_year_month_fmt)
        plt.show()

    def test_optimize (self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete( self.movingAverageAnalyzer.optimize( ))

if __name__ == '__main__':
    unittest.main()
