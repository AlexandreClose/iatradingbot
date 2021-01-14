import matplotlib
import pandas as pd
import schedule
import nest_asyncio

from historicprovider.historic_manager import HistoricManager
from historicprovider.xtb_historic_provider import XtbHistoricProvider
from historicprovider.yahoo_historic_provider import YahooHistoricProvider
from xtbapi.xtbapi_client import *
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')


async def mainProgram( loop ):

    client=xtbClient()

    # process login. this will launch all the websockets and permanent streams (trades, profit, ping, keep_alive)
    await client.login("11712595","TestTest123123") #totoletrader@yopmail.com

    # historic_manager=HistoricManager( loop, 'RIPPLE',XtbHistoricProvider(client) )
    # datas = await historic_manager.get_historical_datas_updated()
    # await historic_manager.plot_history( 'Open' )

    await client.open_buy_trade('BITCOIN',1,0,0)
    await client.close_all_trades( )

async def scheduler( ):
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

def main():

    nest_asyncio.apply()
    # Use asyncio to run sync and async functions
    loop = asyncio.get_event_loop()
    # Performs login
    loop.create_task( scheduler( ) )
    loop.run_until_complete( mainProgram( loop ) ) # Performs sync call, and await result
    loop.run_forever()

if __name__ == "__main__":
    main()



