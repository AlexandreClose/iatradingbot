import asyncio
import unittest
from logging_conf import log
from historicprovider.yahoo_historic_provider import YahooHistoricProvider


class TestYahooFinance(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestYahooFinance, self).__init__(*args, **kwargs)

    def test_send_max_history(self ):
        loop = asyncio.get_event_loop()
        yahoo_finance = YahooHistoricProvider()
        datas = loop.run_until_complete( yahoo_finance.fetch_max_history( 'DASH') )
        log.info( '[YAHOO] : Fetch %s historic data',len(datas))
        self.assertGreater( len(datas), 0)

if __name__ == '__main__':
    unittest.main()