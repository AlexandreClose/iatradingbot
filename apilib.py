####librairie de connexion avec xtb.

import websockets
import asyncio
import json


class apilib:

	def __init__(self):
		#uri websocket xtb demo
		self.uri =  "wss://ws.xtb.com/demo"

	##connexion au serveur xtb
	async def connection(self, user, password):
		command='{"command" : "login","arguments": {"userId": "' + user + '","password": "' + password + '"}}'
		return await self.sendAndReceive(command)
		

	
	###envoie et recvoie les requêtes au serveur xtb
	#retourne la websocket ouverte + la réponse du serveur
	async def sendAndReceive(self, command):
		uri = self.uri
		async with websockets.connect(uri) as websocket:
			sent = await websocket.send(command)
			response = await websocket.recv()

		return [websocket, response]

	




	



