import asyncio
import unittest

from analyzer.exponential_moving_average_analyzer import ExponentialMovingAverageAnalyzer
import matplotlib.pyplot as plt

from historicprovider.historic_manager import HistoricManager
from historicprovider.xtb_historic_provider import XtbHistoricProvider
from xtbapi.xtbapi_client import xtbClient


class TestExponentialMovingAverageAnalyzer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        historic_manager=HistoricManager.instance()
        client=xtbClient()
        loop = asyncio.get_event_loop()
        loop.run_until_complete( client.login("11712595","TestTest123123", False))
        loop.run_until_complete( historic_manager.register_provider( XtbHistoricProvider( client )))
        loop.run_until_complete( historic_manager.register_symbol( 'ETHEREUM'))


    def test_plot_history_dataframe(self):
        loop = asyncio.get_event_loop()
        exponentialMovingAverageAnalyzer = ExponentialMovingAverageAnalyzer()
        ema=loop.run_until_complete( exponentialMovingAverageAnalyzer.compute_exponential_moving_average( 'ETHEREUM', 5, 100 ))
        ax = ema.plot(y= 'ema_Open', color="C1")
        ema.plot(y='sma_Open', color='C2', ax = ax)
        plt.show()

    def test_get_zeros_historic(self):
        loop = asyncio.get_event_loop()
        exponentialMovingAverageAnalyzer = ExponentialMovingAverageAnalyzer()
        ema=loop.run_until_complete( exponentialMovingAverageAnalyzer.compute_trading_signals( 'ETHEREUM', 40 ))

if __name__ == '__main__':
    unittest.main()
