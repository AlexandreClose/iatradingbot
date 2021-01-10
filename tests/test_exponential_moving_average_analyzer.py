import asyncio
import unittest

from analyzer.exponential_moving_average_analyzer import ExponentialMovingAverageAnalyzer
import matplotlib.pyplot as plt

class TestMovingAverageAnalyzer(unittest.TestCase):
    def test_get_history_dataframe(self):
        exponentialMovingAverageAnalyzer = ExponentialMovingAverageAnalyzer('BITCOIN')
        ema = exponentialMovingAverageAnalyzer.compute_exponential_moving_average( 20 )
        ema.plot(x="ctm", y="open", color="C1")
        plt.show()

if __name__ == '__main__':
    unittest.main()