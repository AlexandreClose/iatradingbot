import asyncio
import unittest
from xtbapi.xtbapi_client import xtbClient
from historicprovider.yahoo_historic_provider import YahooHistoricProvider
from historicprovider.historic_provider import HistoricProvider
from historicprovider.xtb_historic_provider import XtbHistoricProvider


class TestHistoryProvider(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestHistoryProvider, self).__init__(*args, **kwargs)
        self.client=xtbClient()
        loop=asyncio.get_event_loop()
        # authenticate the client with no starting of streams
        response = loop.run_until_complete( self.client.login("11712595","TestTest123123",False) )

    async def test_send_max_history(self ):
        historic_provider=HistoricProvider( XtbHistoricProvider(self.client), YahooHistoricProvider() )
        await historic_provider.fetch_and_store_max_history( 'BTC' )


if __name__ == '__main__':
    unittest.main()