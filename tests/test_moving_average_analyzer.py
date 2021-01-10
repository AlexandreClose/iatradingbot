import asyncio
import unittest

from analyzer.moving_average_analyzer import MovingAverageAnalyzer
from xtbapi.xtbapi_client import xtbClient
from historicprovider.yahoo_historic_provider import YahooHistoricProvider
import numpy as np
import matplotlib.pyplot as plt

class TestMovingAverageAnalyzer(unittest.TestCase):
    def test_get_history_dataframe(self):
        movingAverageAnalyzer = MovingAverageAnalyzer('BITCOIN')
        avg_rolling = movingAverageAnalyzer.compute_average_rolling( 100 )
        avg_rolling.plot(x="ctm", y="open", color="C1")
        plt.show()



if __name__ == '__main__':
    unittest.main()