import asyncio
import unittest

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analyzer.moving_average_analyzer import MovingAverageAnalyzer
from manager.historic_manager import historic_manager
from logging_conf import log
from trading_client.trading_client import trading_client


def onresize( event ):
    plt.tight_layout()


class TestMovingAverageAnalyzer(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestMovingAverageAnalyzer, self).__init__(*args, **kwargs)
        self.symbol = 'AMZN.US_9'
        self.movingAverageAnalyzer= MovingAverageAnalyzer( self.symbol, 'ema', 12, 24, False,0.001)
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

    def test_compute_trading_signal_last(self):
        loop = asyncio.get_event_loop()
        df=loop.run_until_complete( self.movingAverageAnalyzer.compute_trading_signals( ) )
        log.info( '[TRADING POSITION] : last ')
        print( df )

    def test_plot_trading_positions(self):
        loop = asyncio.get_event_loop()
        ema=loop.run_until_complete( self.movingAverageAnalyzer.compute_exponential_moving_average( ) )
        trading_positions=loop.run_until_complete( self.movingAverageAnalyzer.compute_trading_signals() )
        log.info( '[TRADING POSITIONS] : %s positions taken', len(trading_positions))
        # ax = ema.plot(y= 'lma_Close', color="C1")
        # ema.plot(y='sma_Close', color='C2',ax=ax)
        ax = ema.plot(y='Open', color='C3')
        ema.plot(y='Close', color='C4',ax=ax)
        trading_positions['color_trading']=np.where(trading_positions['cross_sign_sma_Close_lma_Close']>0, 'green', 'red')
        print( trading_positions )
        plt.scatter(trading_positions.index, trading_positions['sma_Close'],c=trading_positions['color_trading'])
        ax.set_xlim(pd.Timestamp('2020-05-01'), pd.Timestamp('2020-06-05'))
        plt.tight_layout()
        plt.gcf().canvas.mpl_connect('resize_event', onresize)
        plt.show( )

    def test_optimize (self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete( self.movingAverageAnalyzer.optimize( ))

if __name__ == '__main__':
    unittest.main()
