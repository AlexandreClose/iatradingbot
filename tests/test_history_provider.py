import asyncio
import os
import time
import json
import unittest
from collections import OrderedDict

import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import matplotlib.dates as mpl_dates
from mplfinance.original_flavor import candlestick_ohlc

from tick_manager.tick_manager import TickManager
from trading_client.trading_client import TradingClient
from historicprovider.yahoo_historic_provider import YahooHistoricProvider
from historicprovider.historic_manager import HistoricManager
from historicprovider.xtb_historic_provider import XtbHistoricProvider
import matplotlib.pyplot as plt


class TestHistoryProvider(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        historic_manager=HistoricManager.instance()
        tick_manager = TickManager.instance()
        client=TradingClient()
        loop = asyncio.get_event_loop()
        loop.run_until_complete( client.login("11712595","TestTest123123", False))
        loop.run_until_complete( historic_manager.register_provider( XtbHistoricProvider( client )))
        loop.run_until_complete( historic_manager.register_symbol( 'BITCOIN'))
        loop.run_until_complete( tick_manager.register_client ( client ) )
        loop.run_until_complete( tick_manager.register_symbol ( 'BITCOIN' ) )

    def test_plot_history(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete( HistoricManager.instance().plot_history( 'BITCOIN') )


    def test_compare_history_tick_price(self):

        last_minutes_history={}
        last_minutes_tick_prices={}

        if not os.path.isfile('last_minutes_tick_history_comparison/last_minutes_history.json') or not os.path.isfile('last_minutes_tick_history_comparison/last_minutes_tick_prices.json'):
            loop = asyncio.get_event_loop()
            loop.run_until_complete( asyncio.sleep( 650 ) )
            last_minutes_history = loop.run_until_complete( HistoricManager.instance().fetch_time_delta_history( 'BITCOIN', 10) )
            last_minutes_tick_prices = loop.run_until_complete(TickManager.instance().get_tick_prices_time_delta( 'BITCOIN', 10 ))

            with open('last_minutes_tick_history_comparison/last_minutes_history.json', 'w') as fp:
                json.dump(last_minutes_history, fp)

            with open('last_minutes_tick_history_comparison/last_minutes_tick_prices.json', 'w') as fp:
                json.dump(last_minutes_tick_prices, fp)

        else:
            with open('last_minutes_tick_history_comparison/last_minutes_history.json') as f:
                last_minutes_history = json.load(f)
            with open('last_minutes_tick_history_comparison/last_minutes_tick_prices.json') as f:
                last_minutes_tick_prices = json.load(f)

        print( last_minutes_history)
        last_minutes_history = pd.DataFrame(last_minutes_history)
        last_minutes_history.set_index('Date', inplace = True)


        last_minutes_tick_prices = pd.DataFrame(list(last_minutes_tick_prices.values()))
        last_minutes_tick_prices.set_index('timestamp', inplace = True)

        ax = last_minutes_history.plot( y='Open')
        last_minutes_tick_prices.plot( y='bid', ax=ax)
        plt.show()


if __name__ == '__main__':
    unittest.main()