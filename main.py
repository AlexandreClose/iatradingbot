from analyzer.mongodb_connector import mongodb_connector
from xtbapi.xtbapi_client import *
import asyncio
import datetime
from logging_conf import log
import pymongo



async def mainProgram( loop ):
    client=xtbClient()
    


    # process login. this will launch all the websockets and permanent streams (trades, profit, ping, keep_alive)
    await client.login("11712595","TestTest123123") #totoletrader@yopmail.com

    await asyncio.sleep( 2 )
    await getChart(client,"month","DASH")
    await getChart(client,"month","EOS")
    await getChart(client,"half_year","DASH")
    await getChart(client,"half_year","EOS")
    # open a orders
    #await client.open_buy_trade( 'DASH', 1,0,0 )
    #await client.open_order_buy_limit( 'DASH', 1,0,0,12)
    #await client.open_order_buy_stop( 'DASH', 1,0,0,12)
    #await client.open_order_sell_stop( 'DASH', 1,0,0,12)


    #log.info('[TRADES DASH] : %s', await client.get_all_updated_trades( symbol='DASH') )
    #await client.close_all_trades()
    #log.info('[TRADES DASH] : %s', await client.get_all_updated_trades( symbol='DASH') )

    # follow all the tick prices of given array of symbols
    #await client.follow_tick_prices( ['BITCOIN','DASH'])

    # WORK on history


#sync bb with last chart available
#get_type="last" for last data available, get_type="month" for current month data, get_type="half_year" for last 180 days
async def getChart(client,get_type,symbol):
    # #mongodb connection
    mongo=mongodb_connector()
    mongo.connect()
    #set db and collection
    mongo.set_db('history')
    symbol=symbol
    coll=symbol + "_history"
    mongo.set_collection(coll)
    mongo.get_collection().create_index([('ctm', pymongo.ASCENDING)], unique=True, dropDups=True)

    if get_type=="last":
        timestart=mongo.sortdata("ctm",2)[0]['ctm']+60000
        timestop=int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())*1000
    if get_type=="month":
        now=datetime.datetime.now()
        timestart=int(datetime.datetime.now().timestamp()*1000) - int(datetime.datetime.now().timestamp() - datetime.datetime(now.year, now.month,1, 0,0,0).timestamp())*1000
        print(timestart)
        timestop=int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())*1000
    if get_type=="half_year":
        timestart=int((datetime.datetime.now() - datetime.timedelta(days=180)).timestamp())*1000
        timestop=int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())*1000

    historylist= await client.get_history_chart(timestart,timestop,TIME_TYPE.PERIOD_M1,symbol)
    log.debug(historylist['returnData']['rateInfos'])
    if historylist!=[]:
        mongo.collection_insert_multiple(historylist['returnData']['rateInfos'])

def main():
    # Use asyncio to run sync and async functions
    loop = asyncio.get_event_loop()
    # Performs login
    loop.run_until_complete( mainProgram( loop ) ) # Performs sync call, and await result
    loop.run_forever()

if __name__ == "__main__":
    main()



