import asyncio
import quart.flask_patch
import nest_asyncio
import schedule
from hypercorn import Config
from hypercorn.asyncio import serve

from reload.app_reload_service import app_reload_service
from web.create_app import create_app


async def mainProgram():
    await app_reload_service.reload_app_context()

async def scheduler():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


def main():
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    config = Config()
    loop.create_task(serve(create_app(), config))
    loop.create_task(scheduler())
    loop.run_until_complete(mainProgram())  # Performs sync call, and await result
    loop.run_forever()



if __name__ == "__main__":
    main()
