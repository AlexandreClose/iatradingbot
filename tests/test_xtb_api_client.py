import asyncio
import unittest
from trading_client.trading_client import TradingClient, trading_client


class TestTweetAnalyzer(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestTweetAnalyzer, self).__init__(*args, **kwargs)
        self.client=trading_client
        loop=asyncio.get_event_loop()
        # authenticate the client with no starting of streams
        response = loop.run_until_complete( self.client.login("11712595","TestTest123123",False) )
        self.assertTrue(response['status'])

    def test_get_symbol(self ):
        loop=asyncio.get_event_loop()
        response = loop.run_until_complete( self.client.get_symbol( 'BITCOIN') )
        print( response )
        self.assertEqual(response['symbol'],'BITCOIN')

    def test_get_all_symbol(self ):
        loop=asyncio.get_event_loop()
        response = loop.run_until_complete( self.client.get_all_symbols( ) )
        self.assertIn('symbol',response[0].keys())
        for symbol_data in response:
            self.assertIn('symbol',symbol_data.keys())
            print ( symbol_data['symbol'] )

if __name__ == '__main__':
    unittest.main()