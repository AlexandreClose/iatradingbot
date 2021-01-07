from analyzer.mongodb_connector import mongodb_connector
from xtbapi.xtbapi_client import *
import asyncio
import datetime


async def mainProgram( loop ):
    client=xtbClient()
    


    # process login. this will launch all the websockets and permanent streams (trades, profit, ping, keep_alive)
    await client.login("11712595","TestTest123123") #totoletrader@yopmail.com

    await asyncio.sleep( 2 )

    # open a orders
    await client.open_buy_trade( 'DASH', 1,0,0 )
    await client.open_order_buy_limit( 'DASH', 1,0,0,12)
    await client.open_order_buy_stop( 'DASH', 1,0,0,12)
    await client.open_order_sell_stop( 'DASH', 1,0,0,12)


    log.info('[TRADES DASH] : %s', await client.get_all_updated_trades( symbol='DASH') )
    await client.close_all_trades()
    log.info('[TRADES DASH] : %s', await client.get_all_updated_trades( symbol='DASH') )

    # follow all the tick prices of given array of symbols
    await client.follow_tick_prices( ['BITCOIN','DASH'])

    # WORK on history

    # #mongodb connection
    # mongo=mongodb_connector()
    # mongo.connect()
    # #mongodb db and collection creation if needed
    # mongo.create_db('history')

    # #work on charts
    # dt_start = datetime.datetime(2021, 1, 4 ,5,22,00)
    # timestart = int((dt_start - datetime.datetime(1970, 1, 1)).total_seconds())*1000
    # dt_stop = datetime.datetime(2021, 1, 4 ,6,24,00)
    # timestop = int((dt_stop - datetime.datetime(1970, 1, 1)).total_seconds())*1000
    # symbol="DASH"
    # coll=symbol + "_history"

    # historylist= await client.get_history_chart(timestart,timestop,TIME_TYPE.PERIOD_M1,symbol)
    # print(historylist)
    # mongo.create_collection(coll)
    # mongo.set_collection(coll)
    # mongo.collection_insert_multiple(historylist['returnData']['rateInfos'])


def main():
    # Use asyncio to run sync and async functions
    loop = asyncio.get_event_loop()
    # Performs login
    loop.run_until_complete( mainProgram( loop ) ) # Performs sync call, and await result
    loop.run_forever()

if __name__ == "__main__":
    main()



