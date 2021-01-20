import datetime

from trading_client.trading_client import trading_client
from utils.singleton import Singleton
from trading_client.trading_client_enums import *


def extract_time(json):
    try:
        return int(json['Date'])
    except KeyError:
        return 0

@Singleton
class XtbHistoricProvider:

    def __init__(self ):
        self.trading_client = trading_client


    async def fetch_max_history( self, symbol, last_data = None ):
        trading_client=self.trading_client

        timestop=datetime.datetime.now().timestamp()
        datas_1_month_earlier={}
        datas_7_month_earlier={}
        datas_13_month_earlier={}
        datas_max_month_earlier={}
        all_datas = {}

        timestart_1_month_earlier=timestop - datetime.timedelta(days=30).total_seconds()
        timestart_7_month_earlier=timestop - datetime.timedelta(days=210).total_seconds()
        timestart_13_month_earlier=timestop - datetime.timedelta(days=390).total_seconds()
        timestart_max_month_earlier=0

        if last_data is not None:
            last_data_timestamp = last_data['Date']
            if last_data_timestamp >= timestart_1_month_earlier:
                datas_1_month_earlier=await trading_client.get_chart_range_request( last_data_timestamp, timestop, TIME_TYPE.PERIOD_M1, symbol)
            elif last_data_timestamp >= timestart_7_month_earlier:
                datas_1_month_earlier=await trading_client.get_chart_range_request( timestart_1_month_earlier, timestop, TIME_TYPE.PERIOD_M1, symbol)
                datas_7_month_earlier=await trading_client.get_chart_range_request( last_data_timestamp, timestop, TIME_TYPE.PERIOD_M30, symbol)
            elif last_data_timestamp >= timestart_13_month_earlier:
                datas_1_month_earlier=await trading_client.get_chart_range_request( timestart_1_month_earlier, timestop, TIME_TYPE.PERIOD_M1, symbol)
                datas_7_month_earlier=await trading_client.get_chart_range_request( timestart_7_month_earlier, timestop, TIME_TYPE.PERIOD_M30, symbol)
                datas_13_month_earlier=await trading_client.get_chart_range_request( last_data_timestamp, timestop, TIME_TYPE.PERIOD_H4, symbol)
            else:
                datas_1_month_earlier=await trading_client.get_chart_range_request( timestart_1_month_earlier, timestop, TIME_TYPE.PERIOD_M1, symbol)
                datas_7_month_earlier=await trading_client.get_chart_range_request( timestart_7_month_earlier, timestop, TIME_TYPE.PERIOD_M30, symbol)
                datas_13_month_earlier=await trading_client.get_chart_range_request( timestart_13_month_earlier, timestop, TIME_TYPE.PERIOD_H4, symbol)
                datas_max_month_earlier=await trading_client.get_chart_range_request( timestart_max_month_earlier, timestop, TIME_TYPE.PERIOD_D1, symbol)
            all_datas = list(datas_1_month_earlier.values()) + list(datas_7_month_earlier.values()) + list(datas_13_month_earlier.values()) + list(datas_max_month_earlier.values())
        else:
            datas_1_month_earlier=await trading_client.get_chart_range_request( timestart_1_month_earlier, timestop, TIME_TYPE.PERIOD_M1, symbol)
            datas_7_month_earlier=await trading_client.get_chart_range_request( timestart_7_month_earlier, timestop, TIME_TYPE.PERIOD_M30, symbol)
            datas_13_month_earlier=await trading_client.get_chart_range_request( timestart_13_month_earlier, timestop, TIME_TYPE.PERIOD_H4, symbol)
            datas_max_month_earlier=await trading_client.get_chart_range_request( timestart_max_month_earlier, timestop, TIME_TYPE.PERIOD_D1, symbol)
            all_datas = list(datas_1_month_earlier.values()) + list(datas_7_month_earlier.values()) + list(datas_13_month_earlier.values()) + list(datas_max_month_earlier.values())

        all_datas.sort( key = extract_time)

        all_datas_dm = []
        for data in all_datas:
            all_datas_dm.append(self.transform(data))

        return all_datas_dm

    async def fetch_time_delta_history(self, symbol, minutes_number):
        clientXtb = self.trading_client
        timestop = datetime.datetime.now().timestamp()  # now in millisec timestamp
        timestart_n_minutes_earlier = timestop - datetime.timedelta(minutes=minutes_number).total_seconds()
        datas_n_minute_earlier = await clientXtb.get_chart_range_request(timestart_n_minutes_earlier, timestop,
                                                                        TIME_TYPE.PERIOD_M1, symbol)

        all_datas = list(datas_n_minute_earlier.values())
        all_datas.sort( key = extract_time)
        all_datas_dm = []
        for data in all_datas:
            all_datas_dm.append(self.transform(data))
        return all_datas_dm

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

xtb_historic_provider = XtbHistoricProvider.instance()