import asyncio
import nest_asyncio
import schedule
from hypercorn import Config
from hypercorn.asyncio import serve
from quart import Quart

from manager.strategy_manager import strategy_manager
from trading_client.trading_client import trading_client
from web.api_balance_manager import api_balance_manager
from web.api_strategy_manager import api_strategy_manager
from web.api_symbol_manager import api_symbol_manager


async def mainProgram():
    # process login. this will launch all the websockets and permanent streams (trades, profit, ping, keep_alive)
    await trading_client.login("11769869", "TestTest123123")  # totoletrader2@yopmail.com
    await asyncio.sleep( 2 )
    # await strategy_manager.register_strategy('intraday_moving_average', 'RIPPLE')
    await strategy_manager.register_strategy('intraday_moving_average', 'BITCOIN')
    # await strategy_manager.register_strategy('intraday_moving_average', 'BITCOIN')

async def scheduler():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

def main():
    app = Quart(__name__)
    app.register_blueprint(api_balance_manager)
    app.register_blueprint(api_symbol_manager)
    app.register_blueprint(api_strategy_manager)
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    config = Config()
    loop.create_task(serve(app, config))
    loop.create_task(scheduler())
    loop.run_until_complete(mainProgram())  # Performs sync call, and await result
    loop.run_forever()


if __name__ == "__main__":
    main()
