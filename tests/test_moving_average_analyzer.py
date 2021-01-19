import asyncio
import unittest

import numpy as np
import pandas as pd

from logging_conf import log

from analyzer.moving_average_analyzer import MovingAverageAnalyzer
import matplotlib.pyplot as plt

from historicprovider.historic_manager import HistoricManager
from historicprovider.xtb_historic_provider import XtbHistoricProvider
from trading_client.trading_client import TradingClient


class TestMovingAverageAnalyzer(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestMovingAverageAnalyzer, self).__init__(*args, **kwargs)
        self.symbol = 'BITCOIN'
        self.movingAverageAnalyzer= MovingAverageAnalyzer( self.symbol, 'ema', 5, 140, False,2)
        historic_manager=HistoricManager.instance()
        client=TradingClient()
        loop = asyncio.get_event_loop()
        loop.run_until_complete( client.login("11712595","TestTest123123", False))
        loop.run_until_complete( historic_manager.register_provider( XtbHistoricProvider( client )))
        loop.run_until_complete( historic_manager.register_symbol( self.symbol))

    def test_plot_history_dataframe(self):
        loop = asyncio.get_event_loop()
        ema=loop.run_until_complete( self.movingAverageAnalyzer.compute_exponential_moving_average( ) )
        ax = ema.plot(y= 'lma_Close', color="C1")
        ema.plot(y='sma_Close', color='C2', ax = ax)
        plt.show()

    def test_compute_exponential_moving_average_last(self):
        loop = asyncio.get_event_loop()
        df=loop.run_until_complete( self.movingAverageAnalyzer.compute_exponential_moving_average( only_on_last = True) )
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
        ax = ema.plot(y= 'lma_Close', color="C1")
        ema.plot(y='sma_Close', color='C2',ax=ax)
        trading_positions['color_trading']=np.where(trading_positions['cross_sign_sma_Close_lma_Close']>0, 'green', 'red')
        print( trading_positions )
        plt.scatter(trading_positions.index, trading_positions['sma_Close'],c=trading_positions['color_trading'])
        # ax.set_xlim(pd.Timestamp('2018-01-01'), pd.Timestamp('2020-01-01'))
        plt.show( ax=ax)

    def test_optimize (self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete( self.movingAverageAnalyzer.optimize( ))

if __name__ == '__main__':
    unittest.main()
