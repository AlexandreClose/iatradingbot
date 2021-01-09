import asyncio
import unittest
from xtbapi.xtbapi_client import xtbClient
from historicprovider.yahoo_historic_provider import YahooHistoricProvider


class TestYahooFinance(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestYahooFinance, self).__init__(*args, **kwargs)

    def test_send_max_history(self ):
        yahoo_finance = YahooHistoricProvider()
        yahoo_finance.send_max_history( 'DASH')

if __name__ == '__main__':
    unittest.main()