####librairie de connexion avec xtb.

import websocket
import asyncio
import json


class apilib:

	def __init__(self, ws=None):
		#uri websocket xtb demo
		self.uri =  "wss://ws.xtb.com/demo"
		self.ws=ws

	##connexion au serveur xtb
	async def connection(self, user, password):
		command='{"command" : "login","arguments": {"userId": "' + user + '","password": "' + password + '"}}'
		return await self.sendAndReceive(command)
		
	async def getAllSymbols(self,ws):
		command='{"command": "getAllSymbols"}'
		return await self.sendAndReceive(command,ws)

	def connectionClosed(self, ws):
		ws.close()

	
	###envoie et recvoie les requêtes au serveur xtb
	#retourne la websocket ouverte + la réponse du serveur
	async def sendAndReceive(self, command, ws=None):
		uri = self.uri
		if ws == None:
			ws = websocket.create_connection(uri)
			sent =  ws.send(command)
			response =  ws.recv()
		else:
			print ('hola')
			sent =  ws.send(command)
			response =  ws.recv()
		return [ws, response]

	




	



