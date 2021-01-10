import matplotlib
import pandas as pd

from dao.mongodb_client_history import MongoDbClientHistory
from historicprovider.historic_provider import HistoricProvider
from historicprovider.xtb_historic_provider import XtbHistoricProvider
from historicprovider.yahoo_historic_provider import YahooHistoricProvider
from xtbapi.xtbapi_client import *
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')


async def mainProgram( ):
    client=xtbClient()

    # process login. this will launch all the websockets and permanent streams (trades, profit, ping, keep_alive)
    await client.login("11712595","TestTest123123") #totoletrader@yopmail.com

    await asyncio.sleep( 1 )

    clientMongo = MongoDbClientHistory('BITCOIN')
    clientMongo.deleteAll()

    historic_provider=HistoricProvider( XtbHistoricProvider(client),YahooHistoricProvider() )
    # await historic_provider.fetch_and_store_max_history( 'BITCOIN' )
    await historic_provider.fetch_and_store_max_history( 'BITCOIN' )
    # await historic_provider.fetch_and_store_max_history( 'EOS' )


    datas = list(clientMongo.find())
    datas = pd.DataFrame.from_records(datas)
    print(datas)
    datas.plot( x="ctm", y="open")
    plt.show()


def main():
    # Use asyncio to run sync and async functions
    loop = asyncio.get_event_loop()
    # Performs login
    loop.run_until_complete( mainProgram( ) ) # Performs sync call, and await result
    loop.run_forever()

if __name__ == "__main__":
    main()



