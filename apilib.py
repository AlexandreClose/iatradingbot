import websockets
import json
from logging_conf import log

class xtbClient:
	def __init__(self):
		self.stream_session_id=None
		self.uri="wss://ws.xtb.com/demo"
		self.uri_stream= "wss://ws.xtb.com/demoStream"
		self.ws=None
		self.ws_stream_news=None
		self.ws_stream_candles=None
		self.ws_stream_keep_alive=None
		self.ws_stream_trades=None
		self.news=[]
		self.candles=[]
		self.keep_alives=[]
		self.trades=[]
		self.ws_stream_tick_prices_dict = dict() # key : 'BITCOIN' => value : websocket stream tick prices BITCOIN (...)
		self.tick_prices_dict = dict() # key : 'BITCOIN' => value : tick prices BITCOIN (...)


	async def login(self, user, password):
		command = {"command" : "login","arguments": {"userId": user ,"password": password}}
		response = await self.send_and_receive(command)
		assert response['status']==True
		self.stream_session_id = response['streamSessionId']
		log.info( "[LOGIN] : Success. Session open on XTB with stream session id %s", self.stream_session_id )
		log.debug( response )


	async def get_all_symbols(self):
		command = {"command": "getAllSymbols"}
		return await self.send_and_receive(command)

	async def get_calendar(self ):
		command = {"command": "getCalendar"}
		return await self.send_and_receive(command)

	async def get_candles(self, symbol):
		self.ws_stream_candles = await self.open_websocket_stream()
		command = {"command": "getCandles", "streamSessionId": self.stream_session_id, "symbol": symbol}
		return await self.send_and_receive_stream( command, self.ws_stream_candles, self.candles)

	async def get_keep_alive( self ):
		self.ws_stream_keep_alive = await self.open_websocket_stream()
		command = {
			"command": "getKeepAlive",
			"streamSessionId": self.stream_session_id
		}
		return await self.send_and_receive_stream( command, self.ws_stream_keep_alive, self.keep_alives)

	async def get_tick_prices ( self, symbol, min_arrival_time = 5000, max_level = 2 ):
		self.ws_stream_tick_prices_dict[symbol] = await self.open_websocket_stream()
		command = {
			"command": "getTickPrices",
			"streamSessionId": self.stream_session_id,
			"symbol": symbol,
			"minArrivalTime": min_arrival_time,
			"maxLevel": max_level
		}
		self.tick_prices_dict[symbol] = [] # init empty tick prices infos array in memory for this symbol
		await self.send_and_receive_stream( command, self.ws_stream_tick_prices_dict[symbol], self.tick_prices_dict[symbol])

	async def get_news(self ):
		self.ws_stream_news = await self.open_websocket_stream()
		command = {"command": "getNews","streamSessionId": self.stream_session_id}
		return await self.send_and_receive_stream(command, self.ws_stream_news, self.news)

	async def get_trades(self):
		self.ws_stream_trades = await self.open_websocket_stream()
		command = { "command": "getTrades","streamSessionId": self.stream_session_id}
		return await self.send_and_receive_stream( command, self.ws_stream_trades, self.trades)

	async def getStreamingTradeStatusStart(self):
		command={"command": "getTradeStatus","streamSessionId": self.stream_session_id}
		return await self.send_and_receive_stream(command)

	async def getStreamingTradeStatusStop(self):
		command={"command": "stopTradeStatus"}
		return await self.send_and_receive_stream(command)

	async def getStreamingTradesStart(self):
		command = {"command": "getTrades","streamSessionId": self.stream_session_id}
		return await self.send_and_receive_stream(command)

	async def getStreamingTradesStart(self):
		command = {"command": "getTrades","streamSessionId": self.stream_session_id}
		return await self.send_and_receive_stream(command)
	
	async def getStreamingTradesStop(self):
		command = {"command": "stopTrades"}
		return await self.send_and_receive_stream(command)


	async def getStreamingTrades(self, data):
		command = {"command": "trade", "data": data}
		return await self.send_and_receive_stream(command)
	
	async def streamingPing(self, session_id):
		command = {"command": "ping","streamSessionId": self.stream_session_id}
		return await self.send_and_receive_stream(command)



	def connectionClosed(self, ws):
		ws.close()

	async def open_websocket(self):
		self.ws = await websockets.connect(self.uri, max_size=1_000_000_000)

	async def open_websocket_stream(self):
		return await websockets.connect(self.uri_stream, max_size=1_000_000_000)

	###envoie et recvoie les requêtes au serveur xtb
		# retourne la websocket ouverte + la réponse du serveur
	async def send_and_receive(self, json_command):
		command = json.dumps(json_command)
		log.info( "[COMMAND] : " + command )
		if self.ws is None:
			await self.open_websocket()
		try:
			await self.ws.send(command)
			response =  await self.ws.recv()
			return json.loads( response )
		except	Exception:
			self.open_socket()
			await self.ws.send(command)
			response = await self.ws.recv()
			return json.loads( response )

	async def send_and_receive_stream(self, json_command, websocket, resp_array):
		command = json.dumps(json_command)
		log.info( "[COMMAND] : %s", command )
		await websocket.send(command)
		while True:
			response = await websocket.recv()
			log.debug( response )
			resp_array.append( json.loads( response ))

