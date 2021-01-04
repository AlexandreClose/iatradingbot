import logging_conf
from apilib import *
import asyncio

def main():
    client=xtbClient()

    # Use asyncio to run sync and async functions
    loop = asyncio.get_event_loop()

    # Performs login
    loop.run_until_complete( client.login("11676157","TestTest123123") ) # Performs sync call, and await result

    # Open stream for DASH crypto infos
    loop.create_task(client.get_tick_prices( "DASH", min_arrival_time= 2000 )) # Performs async call
    # Open stream for BITCOIN crypto infos
    loop.create_task(client.get_tick_prices( "BITCOIN", min_arrival_time= 2000 )) # Performs async call
    # Open stream for BITCOIN crypto infos

    
    loop.create_task(client.trade_transaction( MODES.BUY, TRANS_TYPES.OPEN, 'DASH', 1,0,0)) # Performs async call


    loop.run_forever()

if __name__ == "__main__":

    main()


