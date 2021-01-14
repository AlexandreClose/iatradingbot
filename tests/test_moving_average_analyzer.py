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
    def test_get_history_dataframe(self):
        client=xtbClient()
        loop = asyncio.get_event_loop()
        loop.create_task( client.login("11712595","TestTest123123") )
        loop.run_until_complete( asyncio.sleep(5))
        historic_manager=HistoricManager( loop, 'BITCOIN',XtbHistoricProvider(client) )
        movingAverageAnalyzer = MovingAverageAnalyzer(historic_manager)
        compute_datas=loop.run_until_complete( movingAverageAnalyzer.compute_moving_average( 200 ))
        ma = compute_datas[0]
        raw= compute_datas[1]
        ax=ma.plot(y= 'Open', color="C1")
        raw.plot(y='Open', color='C2', ax=ax)
        plt.show()


if __name__ == '__main__':
    unittest.main()