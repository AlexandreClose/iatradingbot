import datetime

from xtbapi.xtbapi_client import *
from dao.mongodb_client_history import MongoDbClientHistory

def extract_time(json):
    try:
        return int(json['ctm'])
    except KeyError:
        return 0

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
        all_datas = datas_1_month_earlier.values() + datas_7_month_earlier.values() + datas_13_month_earlier.values() + datas_max_month_earlier.values()

        all_datas.sort( key = extract_time)

        all_datas_dm = []
        for data in all_datas:
            all_datas_dm.append(self.transform(data))


        client.insert_multiple( all_datas_dm )

    async def fetch_time_delta_history(self, symbol, minutes_number):
        clientXtb = self.xtbClient
        timestop = datetime.datetime.now().timestamp() * 1000  # now in millisec timestamp
        timestart_n_minutes_earlier = timestop - datetime.timedelta(minutes=minutes_number).total_seconds() * 1000
        datas_n_minute_earlier = await clientXtb.get_chart_range_request(timestart_n_minutes_earlier, timestop,
                                                                        TIME_TYPE.PERIOD_M1, symbol)

        all_datas = list(datas_n_minute_earlier.values())
        all_datas.sort( key = extract_time)
        all_datas_dm = []
        for data in all_datas:
            all_datas_dm.append(self.transform(data))
        return all_datas_dm



        return datas_1_minute_earlier

    def transform(self, raw_data):
        return {
            "Date":raw_data['ctm']*0.001,
            "DateString":raw_data['ctmString'],
            "Open":raw_data['open']*0.01,
            "Close":(raw_data['close']+raw_data['open'])*0.01,
            "High":(raw_data['open']+raw_data['high'])*0.01,
            "Low":(raw_data['open']+raw_data['low'])*0.01,
            "Volume":raw_data['vol']
        }

