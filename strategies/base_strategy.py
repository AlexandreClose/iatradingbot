import asyncio
import datetime
import enum
import json
import traceback
from asyncio import CancelledError

from quart import session

from analyzer.moving_average_analyzer import MovingAverageAnalyzer
from manager.tick_manager import TickManager
from trading_client.trading_client import TradingClient, admin_trading_client, MODES, trading_clients
from logging_conf import log


class MODE_SELL(enum.Enum):
    ONLY_CLOSE = 0
    TAKE_SHORT = 1


class BaseStrategy:

    def __init__(self, symbol, n_currencies, username='admin' ):
        self.client : TradingClient = trading_clients[username]
        self.symbol=symbol
        self.signals_dict={}
        self.n_currencies = n_currencies; # nb currencies put on this strategy
        self.tick_price_manager : TickManager = TickManager.instance()
        self.last_signal=None
        self.last_date_signal = None
        self.last_type_signal = None #need to fetch last signal type based on current trade
        self.mode_sell = MODE_SELL.ONLY_CLOSE

    async def get_last_signal(self):
        dict_trades =  await self.client.get_all_updated_trades( symbol=self.symbol)
        if len(dict_trades) > 0:
            last_trade = list(dict_trades.values())[-1]
            last_trade_type = last_trade['cmd']
            last_trade_type = MODES( last_trade_type ).name
            if last_trade_type == 'BUY' or last_trade_type == 'BUY_LIMIT' or last_trade_type == 'BUY_STOP':
                self.last_type_signal = 'BUY'
            elif last_trade_type == 'SELL' or last_trade_type == 'SELL_LIMIT' or last_trade_type == 'SELL_STOP':
                self.last_type_signal = 'SELL'
        else:
            self.last_type_signal=None

    async def listen(self):
        await self.get_last_signal()
        while True: # loop if no signal is received since 1 day

            if self.check_last_signal_too_close():
                log.info( "[STRATEGY] for symbol " + self.symbol + ". Last signal is too recent for computation")
                await asyncio.sleep( 60 )
            else:
                try:
                    signal = await self.compute_signal()
                    yield signal
                    if signal == None:
                        log.info( "[STRATEGY] for symbol " + self.symbol + ". NO SIGNAL RECEIVED" )
                    else:
                        log.info( "[STRATEGY] for symbol " + self.symbol + ". SIGNAL : " + str(signal) )


                    if signal:
                            log.info( "[STRATEGY] for symbol " + self.symbol + ". SIGNAL :" )
                            print( signal )
                            self.signals_dict[signal['Date']]=signal
                            self.last_date_signal = signal['Date']
                            if (self.last_type_signal != None and signal['type'] != self.last_type_signal) or (self.last_type_signal == None and signal['type']!= 'SELL'):
                                await self.react( signal )
                    await asyncio.sleep( 60 ) # wait 1 minute for fetching new signal
                except KeyError as e:
                    traceback.print_exc()
                    log.error( e )
                    raise CancelledError

    async def react(self, signal ):
        if signal['type'] == 'BUY':
            tick_price = await self.tick_price_manager.get_last_tick_data_upadted( self.symbol )
            bid = tick_price['bid']
            volume_to_buy = round(self.n_currencies / bid,1)
            await self.client.open_buy_trade( self.symbol, volume_to_buy, 0, 0 )
        if signal['type'] == 'SELL':
            if self.mode_sell == MODE_SELL.ONLY_CLOSE:
                await self.client.close_all_trades(  time_limit = 0, symbol=self.symbol )
            elif self.mode_sell == MODE_SELL.TAKE_SHORT:
                await self.client.close_all_trades(  time_limit = 0, symbol=self.symbol )
                await self.client.open_sell_trade( self.symbol, volume_to_buy, 0, 0)

    def check_last_signal_too_close(self):
        raise NotImplementedError("Must override method check_last_signal_too_close")




