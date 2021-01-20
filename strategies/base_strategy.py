import asyncio
import datetime
import enum

from analyzer.moving_average_analyzer import MovingAverageAnalyzer
from manager.tick_manager import TickManager
from trading_client.trading_client import TradingClient, trading_client, MODES


class MODE_SELL(enum.Enum):
    ONLY_CLOSE = 0
    TAKE_SHORT = 1


class BaseStrategy:

    def __init__(self, symbol, n_currencies ):
        self.client : TradingClient = trading_client
        self.symbol=symbol
        self.signals_dict={}
        self.n_currencies = n_currencies; # nb currencies put on this strategy
        self.tick_price_manager : TickManager = TickManager.instance()
        self.last_signal=None
        self.last_date_signal = None
        self.last_type_signal = None #need to fetch last signal type based on current trade
        self.mode_sell = MODE_SELL.ONLY_CLOSE

    async def _get_last_signal(self):
        dict_trades =  await self.client.get_all_updated_trades( symbol=self.symbol)
        last_trade = list(dict_trades.values())[-1]
        last_trade_type = last_trade['cmd']
        last_trade_type = MODES( last_trade_type ).name
        if last_trade_type == 'BUY' or last_trade_type == 'BUY_LIMIT' or last_trade_type == 'BUY_STOP':
            self.last_type_signal = 'BUY'
        elif last_trade_type == 'SELL' or last_trade_type == 'SELL_LIMIT' or last_trade_type == 'SELL_STOP':
            self.last_type_signal = 'SELL'

    async def listen(self):
        await self._get_last_signal()
        while datetime.today().strftime('%Y-%m-%d') != self.last_date_signal: # loop if no signal is received since 1 day
            signal = await self._compute_signal()
            if signal:
                    self.signals_dict[signal['Date']]=signal
                    self.last_date_signal = signal['Date']
                    if (self.last_type_signal != None and signal['type'] != self.last_type_signal) or (self.last_type_signal == None and signal['type']!= 'SELL'):
                        self.react( signal )
            await asyncio.sleep( 60 ) # wait 1 minute for fetching new signal

    async def react(self, signal ):
        if signal['type'] == 'BUY':
            tick_price = self.tick_price_manager.get_last_tick_data_upadted()
            bid = tick_price['bid']
            volume_to_buy = self.n_currencies / bid
            self.client.open_buy_trade( self.symbol, volume_to_buy, 0, 0 )
        if signal['type'] == 'SELL':
            if self.mode_sell == MODE_SELL.ONLY_CLOSE:
                self.client.close_all_trades(  time_limit = 0, symbol=self.symbol )
            elif self.mode_sell == MODE_SELL.TAKE_SHORT:
                self.client.close_all_trades(  time_limit = 0, symbol=self.symbol )
                self.client.open_sell_trade( self.symbol, volume_to_buy, 0, 0)




