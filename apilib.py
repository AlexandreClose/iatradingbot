import enum
import websockets
import json
from logging_conf import log
import asyncio

class MODES(enum.Enum):
	BUY = 0
	SELL = 1
	BUY_LIMIT = 2
	SELL_LIMIT = 3
	BUY_STOP = 4
	SELL_STOP = 5
	BALANCE = 6
	CREDIT = 7

class TRANS_TYPES(enum.Enum):
	OPEN = 0
	PENDING = 1
	CLOSE = 2
	MODIFY = 3
	DELETE = 4

class TIME_TYPE(enum.Enum):
	PERIOD_M1 = 1
	PERIOD_M5 = 5
	PERIOD_M15 = 15
	PERIOD_M30 = 30
	PERIOD_H1 = 60
	PERIOD_H4 = 240
	PERIOD_D1 = 1440
	PERIOD_W1 = 10080
	PERIOD_MN1 = 43200


class xtbClient:


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
		self.profits=[]
		self.news=[]
		self.candles=[]
		self.keep_alives=[]
		self.trades=dict()
		self.ws_stream_tick_prices_dict = dict() # key : 'BITCOIN' => value : websocket stream tick prices BITCOIN (...)
		self.tick_prices_dict = dict() # key : 'BITCOIN' => value : tick prices BITCOIN (...)

	async def _init_websockets(self):
		self.ws_login=await self._open_websocket()
		self.ws_ping=await self._open_websocket_stream()
		self.ws_stream_news=await self._open_websocket_stream()
		self.ws_stream_candles=await self._open_websocket_stream()
		self.ws_stream_keep_alive=await self._open_websocket_stream()
		self.ws_stream_trades=await self._open_websocket_stream()
		self.ws_stream_profits=await self._open_websocket_stream()


	async def login(self, user, password):
		await self._init_websockets()
		command = {"command" : "login","arguments": {"userId": user ,"password": password}}
		response = await self._send_and_receive(command, self.ws_login)
		assert response['status']==True
		self.stream_session_id = response['streamSessionId']
		log.info( "[LOGIN] : Success. Session open on XTB with stream session id %s", self.stream_session_id )
		log.debug( response )

		# get all existing trades with sync call
		await self._fill_existing_trades()

		loop = asyncio.get_event_loop()
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


	async def get_all_updated_trades(self ):
		return self.trades

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
		return await self._send_and_receive(command, self.ws_trades)

	async def get_calendar(self):
		command = {"command": "getCalendar"}
		return await self._send_and_receive(command, self.ws_trades)

	async def follow_tick_prices( self, symbols ):
		# clear all the followed symbols tick prices
		self.ws_stream_tick_prices_dict.clear()
		self.tick_prices_dict.clear()

		# follow given tick prices
		for symbol in symbols:
			await self._get_tick_prices( symbol )


	async def _get_candles(self, symbol):
		command = {"command": "getCandles", "streamSessionId": self.stream_session_id, "symbol": symbol}
		return await self._send_and_receive_stream(command, self.ws_stream_candles, self.candles)

	async def _get_keep_alive( self ):
		command = {
			"command": "getKeepAlive",
			"streamSessionId": self.stream_session_id
		}
		return await self._send_and_receive_stream(command, self.ws_stream_keep_alive, self.keep_alives)

	async def _get_tick_prices ( self, symbol, min_arrival_time = 5000, max_level = 2 ):
		self.ws_stream_tick_prices_dict[symbol] = await self._open_websocket_stream()
		command = {
			"command": "getTickPrices",
			"streamSessionId": self.stream_session_id,
			"symbol": symbol,
			"minArrivalTime": min_arrival_time,
			"maxLevel": max_level
		}
		self.tick_prices_dict[symbol] = [] # init empty tick prices infos array in memory for this symbol
		asyncio.create_task(self._send_and_receive_stream(command, self.ws_stream_tick_prices_dict[symbol], self.tick_prices_dict[symbol]))

	async def _get_news(self ):
		command = {"command": "getNews","streamSessionId": self.stream_session_id}
		return await self._send_and_receive_stream(command, self.ws_stream_news, self.news)

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
				"openedOnly": True
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
			if response['type'] == 0:
				self.trades[response['order2']]=response
			if response['type'] == 2:
				if response['closed']:
					self.trades[response['position']]=response
			self._remove_closed_trades( )
			log.debug( '[TRADES] total : %s', self.trades )

	async def trade_transaction(self, mode, trans_type, symbol, volume, stop_loss = 0, take_profit = 0, **opt_args  ):

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
		log.debug( response )
		return response

	def _check_volume(self, volume):
		if not isinstance(volume, float):
			try:
				return float(volume)
			except Exception:
				raise ValueError("vol must be float")
		else:
			return volume



	async def getStreamingTradeStatusStart(self):
		command={"command": "getTradeStatus","streamSessionId": self.stream_session_id}
		return await self._send_and_receive_stream(command)

	async def getStreamingTradeStatusStop(self):
		command={"command": "stopTradeStatus"}
		return await self._send_and_receive_stream(command)

	async def getStreamingTradesStart(self):
		command = {"command": "getTrades","streamSessionId": self.stream_session_id}
		return await self._send_and_receive_stream(command)

	async def getStreamingTradesStart(self):
		command = {"command": "getTrades","streamSessionId": self.stream_session_id}
		return await self._send_and_receive_stream(command)

	async def getStreamingTradesStop(self):
		command = {"command": "stopTrades"}
		return await self._send_and_receive_stream(command)


	async def getStreamingTrades(self, data):
		command = {"command": "trade", "data": data}
		return await self._send_and_receive_stream(command)

	async def _get_ping( self ):
		json_command = {"command": "ping","streamSessionId": self.stream_session_id}
		command = json.dumps(json_command)
		while True:
			log.debug( "[COMMAND] : PING" )
			await self.ws_ping.send(command)
			await asyncio.sleep( 8 ) # wait 8 sec for sending ping again

	async def get_history_chart(self,timestart,timeend,period,symbol):
		chartinfo={"end": timeend,"period": period,"start": timestart,"symbol": symbol,"ticks": 0}
		command = {"command": "getChartRangeRequest","arguments": {"info": {"end": timeend,"period": period.value,"start": timestart,"symbol": symbol,"ticks": 0}}}
		return await self._send_and_receive(command, self.ws_login)

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

	async def _send_and_receive_stream(self, json_command, websocket, resp_array):
		command = json.dumps(json_command)
		log.info( "[COMMAND] : %s", command )
		await websocket.send(command)
		while True:
			response = await websocket.recv()
			log.debug( response )
			resp_array.append( json.loads( response ))

	def _remove_closed_trades( self ):
		self.trades = {k: v for k, v in self.trades.items() if v['closed'] == False}

