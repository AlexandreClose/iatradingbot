import asyncio
import unittest

from analyzer.exponential_moving_average_analyzer import ExponentialMovingAverageAnalyzer
import matplotlib.pyplot as plt

from historicprovider.historic_manager import HistoricManager
from historicprovider.xtb_historic_provider import XtbHistoricProvider
from xtbapi.xtbapi_client import xtbClient


class TestMovingAverageAnalyzer(unittest.TestCase):
    def test_get_history_dataframe(self):
        client=xtbClient()
        loop = asyncio.get_event_loop()
        loop.create_task( client.login("11712595","TestTest123123") )
        loop.run_until_complete( asyncio.sleep(5))
        historic_manager=HistoricManager( loop, 'BITCOIN',XtbHistoricProvider(client) )
        exponentialMovingAverageAnalyzer = ExponentialMovingAverageAnalyzer(historic_manager)
        compute_datas=loop.run_until_complete( exponentialMovingAverageAnalyzer.compute_exponential_moving_average( 40 ))
        ema = compute_datas[0]
        raw= compute_datas[1]
        ax=ema.plot(y= 'Open', color="C1")
        raw.plot(y='Open', color='C2', ax=ax)
        plt.show()

if __name__ == '__main__':
    unittest.main()
