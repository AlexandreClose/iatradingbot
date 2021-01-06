import time

import pymongo as pymongo

from logging_conf import log
from apilib import *
import asyncio
import datetime
from analyzer.mongodb_connector import mongodb_connector

async def mainProgram( ):
    client=xtbClient()
    
    #mongodb connection
    mongo=mongodb_connector()
    mongo.connect()
    #mongodb db and collection creation if needed
    mongo.create_db('history')


    # process login. this will launch all the websockets and permanent streams (trades, profit, ping, keep_alive)
    await client.login("11712595","TestTest123123") #totoletrader@yopmail.com
    # open a buy transaction
    order_id = await client.open_trade( 'DASH', 1,0,0)
    await asyncio.sleep( 0.2) #wait 0.2 sec for n
    order_id = await client.open_trade( 'DASH', 1,0,0)
    await asyncio.sleep( 0.2)
    order_id = await client.open_trade( 'DASH', 1,0,0)
    await asyncio.sleep( 0.2)
    log.info('[ TRADES ] : %s', await client.get_all_updated_trades() )

    await client.close_all_trades( )

    # follow all the tick prices of given array of symbols
    #await client.follow_tick_prices( ['BITCOIN','DASH'])

    #work on charts
    dt_start = datetime.datetime(2021, 1, 4 ,5,22,00)
    timestart = int((dt_start - datetime.datetime(1970, 1, 1)).total_seconds())*1000
    dt_stop = datetime.datetime(2021, 1, 4 ,6,24,00)
    timestop = int((dt_stop - datetime.datetime(1970, 1, 1)).total_seconds())*1000
    symbol="DASH"
    coll=symbol + "_history"

    historylist= await client.get_history_chart(timestart,timestop,TIME_TYPE.PERIOD_M1,symbol)
    print(historylist)
    mongo.create_collection(coll)
    mongo.set_collection(coll)
    mongo.collection_insert_multiple(historylist['returnData']['rateInfos'])



    # async wait
    #await asyncio.sleep( 3 )
    # check profit of open trade
    #log.info('[ TRADES ] : %s', await client.get_all_updated_trades() ) # the trades will display a profit X
    #await asyncio.sleep( 10 )
    # check profit of open trade after 10 sec
    #log.info('[ TRADES AFTER 10 SEC ] : %s', await client.get_all_updated_trades() )



def main():

    # Use asyncio to run sync and async functions
    loop = asyncio.get_event_loop()
    # Performs login
    loop.run_until_complete( mainProgram( ) ) # Performs sync call, and await result
    loop.run_forever()

if __name__ == "__main__":
    main()



