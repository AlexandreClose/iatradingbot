#API_Lib.py>

import websockets
import asyncio

import json

class apilib:


	async def connection(user, password):
		command='{"command" : "login","arguments": {"userId": "' + user + '","password": "' + password + '"}}'
		print (command)
		uri = "wss://ws.xtb.com/demo"
		async with websockets.connect(uri) as websocket:
			sent = await websocket.send(command)
			print(sent)
			response = await websocket.recv()

		print(response)




	



