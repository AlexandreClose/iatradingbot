import websockets
import json


class xtbClient:
	def __init__(self):
		self.stream_session_id=None
		self.uri="wss://ws.xtb.com/demo"
		self.uri_stream= "wss://ws.xtb.com/demoStream"
		self.ws=None
		self.ws_stream=None

	async def login(self, user, password):
		command = {"command" : "login","arguments": {"userId": user ,"password": password}}
		response = await self.send_and_receive(command)
		self.stream_session_id = response['streamSessionId']
		return response

	async def getAllSymbols(self):
		command = {"command": "getAllSymbols"}
		return await self.send_and_receive(command)

	async def getCalendar(self ):
		command = {"command": "getCalendar"}
		return await self.send_and_receive(command)

	async def getStreamingCandles(self, symbol):
		command = {"command": "getCandles", "streamSessionId": self.stream_session_id, "symbol": symbol}
		return await self.send_and_receive(command)

	async def getStreamingNews(self ):
		await self.open_websocket_stream()
		command = {"command": "getNews","streamSessionId": self.stream_session_id}
		return await self.send_and_receive_stream(command)

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
		self.ws_stream = await websockets.connect(self.uri_stream, max_size=1_000_000_000)

		###envoie et recvoie les requêtes au serveur xtb
		# retourne la websocket ouverte + la réponse du serveur
	async def send_and_receive(self, json_command):
		command = json.dumps(json_command)
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

	async def send_and_receive_stream(self, json_command):
		command = json.dumps(json_command)
		if self.ws_stream is None:
			await self.open_websocket_stream()
		try:
			await self.ws_stream.send(command)
			response =  await self.ws_stream.recv()
			return json.loads( response )
		except	Exception:
			self.open_websocket_stream()
			await self.ws_stream.send(command)
			response = await self.ws_stream.recv()
			return json.loads( response )
