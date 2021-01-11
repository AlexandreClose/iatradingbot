import asyncio
import unittest

from analyzer.exponential_moving_average_analyzer import ExponentialMovingAverageAnalyzer
import matplotlib.pyplot as plt

class TestMovingAverageAnalyzer(unittest.TestCase):
    def test_get_history_dataframe(self):
        exponentialMovingAverageAnalyzer = ExponentialMovingAverageAnalyzer('BITCOIN')
        compute_datas=exponentialMovingAverageAnalyzer.compute_exponential_moving_average( 20 )
        ema = compute_datas[0]
        raw_datas=compute_datas[1]
        xema=ema['ctm']
        yema=ema['open']
        yraw=raw_datas['open']
        plt.plot(xema, yema, color="C1")
        plt.plot(xema, yraw, color="green")
        plt.show()

if __name__ == '__main__':
    unittest.main()
