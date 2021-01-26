import asyncio
import nest_asyncio
import schedule
from hypercorn import Config
from hypercorn.asyncio import serve
from quart import Quart

from manager.balance_manager import balance_manager
from manager.symbol_manager import symbol_manager
from trading_client.trading_client import trading_client
from web.api_balance_manager import api_balance_manager
from web.api_symbol_manager import api_symbol_manager


async def mainProgram():
    # process login. this will launch all the websockets and permanent streams (trades, profit, ping, keep_alive)
    await trading_client.login("11769869", "TestTest123123")  # totoletrader2@yopmail.com

    await symbol_manager.register_symbol( 'ETHEREUM')



async def scheduler():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


def main():
    app = Quart(__name__)
    app.register_blueprint(api_balance_manager)
    app.register_blueprint(api_symbol_manager)
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    config = Config()
    loop.create_task(serve(app, config))
    loop.create_task(scheduler())
    loop.run_until_complete(mainProgram())  # Performs sync call, and await result
    loop.run_forever()


if __name__ == "__main__":
    main()
