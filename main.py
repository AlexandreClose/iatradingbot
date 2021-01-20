import asyncio
import threading

from flask import Flask
import nest_asyncio
import schedule
from gevent import thread

from historicprovider.historic_manager import HistoricManager
from historicprovider.xtb_historic_provider import XtbHistoricProvider
from symbol_manager.symbol_manager import symbol_manager
from tick_manager.tick_manager import TickManager
from trading_client.trading_client import TradingClient, trading_client


async def mainProgram():
    # process login. this will launch all the websockets and permanent streams (trades, profit, ping, keep_alive)
    await trading_client.login("11769869", "TestTest123123")  # totoletrader@yopmail.com

    await symbol_manager.register_symbol( 'ETHEREUM')



async def scheduler():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

def run_flask():
    app = Flask(__name__)
    app.run(debug=False,port = "1234")


def main():

    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    loop.create_task(scheduler())
    loop.run_until_complete(mainProgram())  # Performs sync call, and await result
    loop.run_forever()


if __name__ == "__main__":
    threading.Thread(target=run_flask, args=()).start()
    main()
