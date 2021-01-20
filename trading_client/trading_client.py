import datetime
import time
import websockets
import json
from logging_conf import log
import asyncio

from trading_client.trading_client_enums import *
from utils.singleton import Singleton


def extract_time(json):
    try:
        return int(json['timestamp'])
    except KeyError:
        return 0

@Singleton
class TradingClient():

	def __init__(self):
		self.stream_session_id=None
		self.uri="wss://ws.xtb.com/demo"
		self.uri_stream= "wss://ws.xtb.com/demoStream"
		self.ws_login=None
		self.ws_trades=None
		self.ws_stream_news=None
		self.ws_stream_candles=None
		self.ws_stream_keep_alive=None
		self.ws_stream_trades=None
		self.ws_stream_balances=None
		self.news=[]
		self.candles=[]
		self.keep_alives=[]
		self.tick_prices_dict=dict()
		self.trades=dict()
		self.balances=[]
		self.ws_stream_tick_prices_dict = dict() # key : 'BITCOIN' => value : websocket stream tick prices BITCOIN (...)

	async def _init_websockets(self):
		self.ws_login=await self._open_websocket()
		self.ws_ping=await self._open_websocket_stream()
		self.ws_stream_news=await self._open_websocket_stream()
		self.ws_stream_candles=await self._open_websocket_stream()
		self.ws_stream_keep_alive=await self._open_websocket_stream()
		self.ws_stream_trades=await self._open_websocket_stream()
		self.ws_stream_profits=await self._open_websocket_stream()
		self.ws_stream_balances=await self._open_websocket_stream()


	async def login(self, user, password, run_stream = True):
		await self._init_websockets()
		command = {"command" : "login","arguments": {"userId": user ,"password": password}}
		response = await asyncio.ensure_future( self._send_and_receive(command, self.ws_login) )
		assert response['status']==True
		self.stream_session_id = response['streamSessionId']
		log.info( "[LOGIN] : Success. Session open on XTB with stream session id %s", self.stream_session_id )
		await asyncio.ensure_future( self._fill_existing_trades())

		if run_stream:

			loop = asyncio.get_event_loop()
			# track all balances with stream
			asyncio.run_coroutine_threadsafe( self._get_balances(), loop)
			# regularily ping the server with stream
			asyncio.run_coroutine_threadsafe( self._get_ping(), loop)
			# track all trades changes with stream
			asyncio.run_coroutine_threadsafe(self._track_trades_stream(), loop)
			# track all profit of trades with stream
			asyncio.run_coroutine_threadsafe(self._get_profits(), loop)
			# track all keep_alive with stream
			asyncio.run_coroutine_threadsafe( self._get_keep_alive(), loop)
			# track all news with stream
			asyncio.run_coroutine_threadsafe( self._get_news(), loop)

		return response

	async def logout(self):
		command = {
			"command": "logout"
		}
		response = await asyncio.ensure_future( self._send_and_receive(command, self.ws_login) )


	### BUY
	async def open_buy_trade(self, symbol, volume, stop_loss, take_profit ):
		response = await asyncio.ensure_future( self._trade_transaction( MODES.BUY, TRANS_TYPES.OPEN, symbol, volume, stop_loss, take_profit ))
		order_id = response['returnData']['order']
		log.info( "[OPEN BUY] : %s", order_id )
		await self.get_all_updated_trades( )
		return order_id

	async def open_order_buy_limit( self, symbol, volume, stop_loss, take_profit, price ):
		response = await asyncio.ensure_future( self._trade_transaction( MODES.BUY_LIMIT, TRANS_TYPES.OPEN, symbol, volume, stop_loss, take_profit, price=price ))
		order_id = response['returnData']['order']
		log.info( "[OPEN BUY LIMIT] : %s", order_id )
		return order_id

	async def open_order_buy_stop( self, symbol, volume, stop_loss, take_profit, price ):
		response = await asyncio.ensure_future( self._trade_transaction( MODES.BUY_STOP, TRANS_TYPES.OPEN, symbol, volume, stop_loss, take_profit, price=price ))
		order_id = response['returnData']['order']
		log.info( "[OPEN BUY STOP] : %s", order_id )
		return order_id

	### SELL
	async def open_sell_trade(self, symbol, volume, stop_loss, take_profit ):
		response = await asyncio.ensure_future( self._trade_transaction( MODES.SELL, TRANS_TYPES.OPEN, symbol, volume, stop_loss, take_profit ))
		order_id = response['returnData']['order']
		log.info( "[OPEN SELL] : %s", order_id )
		return order_id

	async def open_order_sell_limit( self, symbol, volume, stop_loss, take_profit, price ):
		response = await asyncio.ensure_future(  self._trade_transaction( MODES.SELL_LIMIT, TRANS_TYPES.OPEN, symbol, volume, stop_loss, take_profit, price=price ))
		order_id = response['returnData']['order']
		log.info( "[OPEN SELL LIMIT] : %s", order_id )
		return order_id

	async def open_order_sell_stop( self, symbol, volume, stop_loss, take_profit, price ):
		response = await asyncio.ensure_future(  self._trade_transaction( MODES.SELL_STOP, TRANS_TYPES.OPEN, symbol, volume, stop_loss, take_profit, price=price ))
		order_id = response['returnData']['order']
		log.info( "[OPEN SELL STOP] : %s", order_id )
		return order_id

	async def close_trade(self, order_id, time_limit = 5): #time_limit is infinity by default
		passed_time = 0
		retry = True
		while retry == True:
			if order_id in self.trades:
				trade=self.trades[order_id]
				if 'cmd' in trade and trade['cmd'] in (0,1):
					# this a position to close
					response = await self._trade_transaction( MODES(trade['cmd']),
															  TRANS_TYPES.CLOSE,
															  trade['symbol'],
															  trade['volume'],
															  price = trade['close_price'],
															  order= trade['position'] )
				else:
					# this is an order to cancel
					response = await self._trade_transaction( MODES(trade['cmd']),
															  TRANS_TYPES.DELETE,
															  trade['symbol'],
															  trade['volume'],
															  price = trade['close_price'],
															  order= trade['position'] )
				if 'errorCode' not in response:
					order_id = response['returnData']['order']
					log.info( "[CLOSE TRADE] : %s", order_id )
					return order_id
				else:
					log.error("[ERROR CLOSE TRADE] : Retry closing order " + str(order_id) )
					# for reload of trades
					await self._fill_existing_trades()
					await asyncio.sleep( 0.5 ) # wait 200 ms for trying to close the trade
					passed_time += 0.5
					if time_limit > 0:
						if passed_time > time_limit:
							retry = False


	async def close_all_trades(self, time_limit = 0, **opt_args_filter ):
		trades = self.trades
		#filter if arg filters are given
		if opt_args_filter is not None:
			if 'profit' in opt_args_filter:
				profit = opt_args_filter['profit']
				if profit is not None:
					trades = dict((k, v) for (k, v) in trades.items() if 'profit' in v and v['profit'] > profit)
			if 'symbol' in opt_args_filter:
				symbol = opt_args_filter['symbol']
				if symbol is not None:
					trades = dict((k, v) for (k, v) in trades.items() if 'symbol' in v and v['symbol'] == symbol)
		closed_order_ids = []
		for k in list(trades.keys()):
			order_id = await asyncio.ensure_future(self.close_trade( k, time_limit ))
			closed_order_ids.append( order_id )
			await asyncio.sleep( 0.2 ) # wait 0.2 sec for websocket not being killed by backend
		return closed_order_ids

	async def get_tick_prices(self, symbol ):
		if symbol in self.tick_prices_dict :
			return self.tick_prices_dict[symbol]
		else:
			return {}

	async def get_tick_prices_time_delta(self, symbol, minute_timedelta = 1 ):
		tick_prices = self.tick_prices_dict[symbol]
		for timestamp in tick_prices.keys():
			if timestamp > datetime.datetime.now().timestamp() - datetime.timedelta( minutes= minute_timedelta).total_seconds():
				return {k:tick_prices[k] for k in tick_prices.keys() if k >= timestamp}

	async def get_all_updated_trades(self, **opt_args_filter ):
		trades = self.trades
		if opt_args_filter is not None:
			if 'profit' in opt_args_filter:
				profit = opt_args_filter['profit']
				if profit is not None:
					trades = dict((k, v) for (k, v) in trades.items() if 'profit' in v and v['profit'] > profit)
			if 'symbol' in opt_args_filter:
				symbol = opt_args_filter['symbol']
				if symbol is not None:
					trades = dict((k, v) for (k, v) in trades.items() if 'symbol' in v and v['symbol'] == symbol)
		trades = dict((k, v) for (k, v) in trades.items() if ('state' in v and v['state'] != 'Deleted') or ('state' not in v))
		return trades

	async def get_last_updated_balance(self, **opt_args_filter ):
		balances = self.balances
		return balances[-1]

	async def get_symbol(self, symbol):
		command = {
			"command": "getSymbol",
			"arguments": {
				"symbol": symbol
			}
		}
		response = await self._send_and_receive(command, self.ws_login)
		log.debug( response['returnData'] )
		return response['returnData']

	async def get_all_symbols(self):
		command = {"command": "getAllSymbols"}
		response = await self._send_and_receive(command, self.ws_login)
		return response['returnData']

	async def get_calendar(self):
		command = {"command": "getCalendar"}
		response = await self._send_and_receive(command, self.ws_login)
		return response['returnData']

	async def follow_tick_prices( self, symbols ):
		# clear all the followed symbols tick prices
		self.ws_stream_tick_prices_dict.clear()
		self.tick_prices_dict.clear()

		# follow given tick prices
		for symbol in symbols:
			await self._get_tick_prices( symbol )


	async def _get_candles(self, symbol):
		command = {"command": "getCandles", "streamSessionId": self.stream_session_id, "symbol": symbol}
		return await self._send_and_receive_stream(command, 'CANDLES', self.ws_stream_candles, self.candles)

	async def _get_keep_alive( self ):
		command = {
			"command": "getKeepAlive",
			"streamSessionId": self.stream_session_id
		}
		return await self._send_and_receive_stream(command, 'KEEP_ALIVE', self.ws_stream_keep_alive, self.keep_alives)

	async def _get_balances( self ):
		command = {
			"command": "getBalance",
			"streamSessionId": self.stream_session_id
		}
		return await self._send_and_receive_stream(command, 'BALANCE', self.ws_stream_balances, self.balances)

	async def _get_tick_prices ( self, symbol, min_arrival_time = 5000, max_level = 2 ):
		self.ws_stream_tick_prices_dict[symbol] = await self._open_websocket_stream()
		command = {
			"command": "getTickPrices",
			"streamSessionId": self.stream_session_id,
			"symbol": symbol,
			"minArrivalTime": min_arrival_time,
			"maxLevel": max_level
		}
		self.tick_prices_dict[symbol] = {} # init empty tick prices infos array in memory for this symbol
		asyncio.create_task(self._send_and_receive_ticks_stream(command, 'TICK_PRICES', self.ws_stream_tick_prices_dict[symbol], self.tick_prices_dict[symbol] ) )

	async def _get_news(self ):
		command = {"command": "getNews","streamSessionId": self.stream_session_id}
		return await self._send_and_receive_stream(command, 'NEWS' ,self.ws_stream_news, self.news)

	async def _get_profits(self):
		command = json.dumps({
			"command": "getProfits",
			"streamSessionId": self.stream_session_id
		})
		log.info( "[COMMAND] : %s", command )
		await self.ws_stream_profits.send(command)
		while True:
			response = await self.ws_stream_profits.recv()
			response = json.loads( response )['data']
			if  response['order2'] in self.trades:
				self.trades[response['order2']]['profit']=response['profit']
				self.trades[response['order2']]['marketValue']=response['marketValue']
				self.trades[response['order2']]['profitCalcPrice']=response['profitCalcPrice']
				self.trades[response['order2']]['profitRecalcPrice']=response['profitRecalcPrice']

	async def _fill_existing_trades(self):
		command = {
			"command": "getTrades",
			"arguments": {
				"openedOnly": False
			}
		}
		existing_trades = await self._send_and_receive(command, websocket=self.ws_login)
		for trade in existing_trades['returnData']:
			self.trades[trade['order2']]=trade
		log.debug( "[TRADES] existing : %s", self.trades)


	async def _track_trades_stream(self):
		command = { "command": "getTrades","streamSessionId": self.stream_session_id}
		log.info( "[COMMAND] : %s", command )
		await self.ws_stream_trades.send( json.dumps( command ) )
		while True:
			response = await self.ws_stream_trades.recv()
			response = json.loads( response )['data']
			if response['type'] in (0,1,3):
				self.trades[response['order2']]=response
			if response['type'] == 2:
				if response['closed']:
					self.trades[response['position']]=response
			self._remove_closed_trades( )
			log.debug( '[TRADES] total : %s', self.trades )


	async def _trade_transaction(self, mode, trans_type, symbol, volume, stop_loss = 0, take_profit = 0, **opt_args  ):

		#some controls
		accepted_values = ['order', 'price', 'expiration', 'customComment',
						   'offset']
		assert all([val in accepted_values for val in opt_args.keys()])
		stop_loss = float(stop_loss)
		take_profit = float(take_profit)
		self._check_volume( volume )
		conversion_mode = {MODES.BUY.value: 'ask', MODES.SELL.value: 'bid'}

		if "price" not in opt_args:
			symbol_current = await self.get_symbol( symbol )
			opt_args['price'] = symbol_current[conversion_mode[mode.value]]

		#Basic infos for opening trade
		infos = {
			"cmd": mode.value,
			"sl": stop_loss,
			"symbol": symbol,
			"tp": take_profit,
			"type": trans_type.value,
			"volume": volume
		}

		#Optional infos for opening trade
		infos.update( opt_args )

		command = {
			"command": "tradeTransaction",
			"arguments": {
				"tradeTransInfo": infos
			}
		}
		response = await self._send_and_receive(command, self.ws_login)
		# intialize the transaction in the trades dict;
		if 'returnData' in response and 'order' in response['returnData'] and 'errorCode' not in response['returnData']:
			self.trades[response['returnData']['order']]={
				'symbol':symbol,
				'volume':volume,
				'cmd':mode.value,
				'close_price': opt_args['price'],
				'order':response['returnData']['order'],
				'position':response['returnData']['order'],
				'order2':response['returnData']['order']
				} # init trade in trade dict
		return response

	def _check_volume(self, volume):
		if not isinstance(volume, float):
			try:
				return float(volume)
			except Exception:
				raise ValueError("vol must be float")
		else:
			return volume

	async def _get_ping( self ):
		json_command = {"command": "ping","streamSessionId": self.stream_session_id}
		command = json.dumps(json_command)
		while True:
			log.debug( "[COMMAND] : PING" )
			await self.ws_ping.send(command)
			await asyncio.sleep( 8 ) # wait 8 sec for sending ping again

	async def get_chart_range_request(self,timestart,timeend,period,symbol):
		command = {"command": "getChartRangeRequest","arguments": {"info": {"end": timeend*1000,"period": period.value,"start": timestart*1000,"symbol": symbol,"ticks": 0}}}
		response = await self._send_and_receive(command, self.ws_login)
		response = response['returnData']['rateInfos']
		dictHistory = {}
		for data_history in response:
			dictHistory[data_history['ctm']]=data_history
		return dictHistory

	async def _open_websocket(self):
		return await websockets.connect(self.uri, max_size=1_000_000_000)

	async def _open_websocket_stream(self):
		return await websockets.connect(self.uri_stream, max_size=1_000_000_000)

	###envoie et recvoie les requêtes au serveur xtb
		# retourne la websocket ouverte + la réponse du serveur
	async def _send_and_receive(self, json_command, websocket):
		command = json.dumps(json_command)
		log.info( "[COMMAND] : " + command )
		await websocket.send(command)
		response = await websocket.recv()
		return json.loads( response )

	async def _send_and_receive_stream(self, json_command, label, websocket, resp_array, timestamp = False, timestamp_as_key = False ):
		command = json.dumps(json_command)
		log.info( "[COMMAND] : %s - %s", label, command )
		await websocket.send(command)
		while True:
			try :
				response = await websocket.recv()
				log.debug( "[STREAM] : %s - %s", label, response )
				response = json.loads( response )['data']
				if timestamp:
					response['timestamp']=time.time()
				if timestamp_as_key:
					resp_array[response['timestamp']]=response
				else:
					resp_array.append( response )
			except Exception as er:
				log.error( er )

	async def _send_and_receive_ticks_stream(self, json_command, label, websocket, resp_array ):
		command = json.dumps(json_command)
		log.info( "[COMMAND] : %s - %s", label, command )
		await websocket.send(command)
		while True:
			response = await websocket.recv()
			log.debug( "[STREAM] : %s - %s", label, response )
			response = json.loads( response )['data']
			if response['level'] == 0 :
				response['timestamp'] = response['timestamp']*0.001
				resp_array[response['timestamp']]=response

	def _remove_closed_trades( self ):
		self.trades = {k: v for k, v in self.trades.items() if v['closed'] == False}
		self.trades = {k: v for k, v in self.trades.items() if v['state'] != 'Deleted'}

trading_client = TradingClient.instance()