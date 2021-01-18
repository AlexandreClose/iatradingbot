import nest_asyncio
import schedule

from historicprovider.historic_manager import HistoricManager
from historicprovider.xtb_historic_provider import XtbHistoricProvider
from tick_manager.tick_manager import TickManager
from xtbapi.xtbapi_client import *


async def mainProgram(loop):
    client = xtbClient()

    # process login. this will launch all the websockets and permanent streams (trades, profit, ping, keep_alive)
    await client.login("11712595", "TestTest123123")  # totoletrader@yopmail.com

    historic_manager = HistoricManager.instance()
    tick_manager = TickManager.instance()

    await historic_manager.register_provider(XtbHistoricProvider(client))
    await historic_manager.register_symbol('ETHEREUM')

    await tick_manager.register_client(client)
    await tick_manager.register_symbol('ETHEREUM')

    await client.open_buy_trade( 'ETHEREUM', 1, 0 ,0)
    await client.close_all_trades()
    await client.get_all_updated_trades( )


async def scheduler():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


def main():
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    loop.create_task(scheduler())
    loop.run_until_complete(mainProgram(loop))  # Performs sync call, and await result
    loop.run_forever()


if __name__ == "__main__":
    main()
