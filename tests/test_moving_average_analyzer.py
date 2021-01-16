import asyncio
import unittest

from analyzer.moving_average_analyzer import MovingAverageAnalyzer
from historicprovider.historic_manager import HistoricManager
from historicprovider.xtb_historic_provider import XtbHistoricProvider
from xtbapi.xtbapi_client import xtbClient
from historicprovider.yahoo_historic_provider import YahooHistoricProvider
import numpy as np
import matplotlib.pyplot as plt

class TestMovingAverageAnalyzer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        historic_manager=HistoricManager.instance()
        client=xtbClient()
        loop = asyncio.get_event_loop()
        loop.run_until_complete( client.login("11712595","TestTest123123", False))
        loop.run_until_complete( historic_manager.register_provider( XtbHistoricProvider( client )))
        loop.run_until_complete( historic_manager.register_symbol( 'BITCOIN'))



    def test_get_history_dataframe(self):
            loop = asyncio.get_event_loop()
            movingAverageAnalyzer = MovingAverageAnalyzer()
            compute_datas=loop.run_until_complete( movingAverageAnalyzer.compute_moving_average( 'BITCOIN',200 ))
            ma = compute_datas
            ax=ma.plot(y= 'ma_Open', color="C1")
            ma.plot(y='Open', color='C2', ax=ax)
            plt.show()


if __name__ == '__main__':
    unittest.main()