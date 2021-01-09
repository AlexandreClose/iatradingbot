import datetime

import pandas as pd
import yfinance as yf
from xtbapi.xtbapi_client import *
from analyzer.mongodb_client_history import MongoDbClientHistory

class XtbHistoricProvider():

    def __init__(self, xtbClient):
        self.xtbClient = xtbClient

    async def send_max_history( self, symbol):

        client=MongoDbClientHistory( symbol )
        clientXtb=self.xtbClient
        timestop=datetime.datetime.now().timestamp()*1000 # now in millisec timestamp
        # get the recent PERIOD_M1 last month

        timestart_1_month_earlier=timestop - datetime.timedelta(days=30).total_seconds()*1000
        timestart_7_month_earlier=timestop - datetime.timedelta(days=210).total_seconds()*1000
        timestart_13_month_earlier=timestop - datetime.timedelta(days=390).total_seconds()*1000
        timestart_max_month_earlier=0

        datas_1_month_earlier=await clientXtb.get_chart_range_request( timestart_1_month_earlier, timestop, TIME_TYPE.PERIOD_M1, symbol)
        datas_7_month_earlier=await clientXtb.get_chart_range_request( timestart_7_month_earlier, timestop, TIME_TYPE.PERIOD_M30, symbol)
        datas_13_month_earlier=await clientXtb.get_chart_range_request( timestart_13_month_earlier, timestop, TIME_TYPE.PERIOD_H4, symbol)
        datas_max_month_earlier=await clientXtb.get_chart_range_request( timestart_max_month_earlier, timestop, TIME_TYPE.PERIOD_D1, symbol)
        all_datas = datas_1_month_earlier + datas_7_month_earlier + datas_13_month_earlier + datas_max_month_earlier

        client.insert_multiple( all_datas )