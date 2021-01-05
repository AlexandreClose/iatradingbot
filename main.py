import time

import logging_conf
from apilib import *
import asyncio
import datetime

async def mainProgram( ):
    client=xtbClient()
    await client.login("11676157","TestTest123123")
    #loop.create_task(client.get_tick_prices( "DASH", min_arrival_time= 2000 )) # Performs async call
    # Open stream for BITCOIN crypto infos
    #loop.create_task(client.get_tick_prices( "BITCOIN", min_arrival_time= 2000 )) # Performs async call
    # Open stream for BITCOIN crypto infos
    await client.trade_transaction( MODES.BUY, TRANS_TYPES.OPEN, 'DASH', 1,0,0, customComment="titi")
    time.sleep(0.200)
    await client.trade_transaction( MODES.BUY, TRANS_TYPES.OPEN, 'DASH', 1,0,0, customComment="titi")
    time.sleep(0.200)
    await client.trade_transaction( MODES.BUY, TRANS_TYPES.OPEN, 'DASH', 1,0,0, customComment="titi")
    time.sleep(0.200)

    dt_start = datetime.datetime(2021, 1, 4 ,5,22,00)
    timestart = int((dt_start - datetime.datetime(1970, 1, 1)).total_seconds())*1000
    dt_stop = datetime.datetime(2021, 1, 4 ,6,24,00)
    timestop = int((dt_stop - datetime.datetime(1970, 1, 1)).total_seconds())*1000

    asyncio.create_task(client.get_history_chart(timestart,timestop,TIME_TYPE.PERIOD_M1,"EURUSD"))



def main():

    # Use asyncio to run sync and async functions
    loop = asyncio.get_event_loop()

    # Performs login
    loop.run_until_complete( mainProgram( ) ) # Performs sync call, and await result

    loop.run_forever()

if __name__ == "__main__":

    main()


