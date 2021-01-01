import websockets


class xtbClient:

    def __init__(self):
        self.uri = "wss://ws.xtb.com/demo"
        self.ws = None

    async def login(self, user, password):
        command = '{"command" : "login","arguments": {"userId": "' + user + '","password": "' + password + '"}}'
        return await self.sendAndReceive(command)

    async def getAllSymbols(self):
        command = '{"command": "getAllSymbols"}'
        return await self.sendAndReceive(command)

    async def getCalendar(self, ws):
        command = '{"command": "getCalendar"}'
        return await self.sendAndReceive(command)

    async def getCandles(self, ws, session_id, symbol):
        command = '{"command": "getCandles", "streamSessionId": "' + session_id + '", "symbol": "' + symbol + '"}'
        return await self.sendAndReceive(command)

    def connectionClosed(self, ws):
        ws.close()

    async def open_socket(self):
        self.ws = await websockets.connect(self.uri, max_size=1_000_000_000)

    ###envoie et recvoie les requêtes au serveur xtb
    # retourne la websocket ouverte + la réponse du serveur
    async def sendAndReceive(self, command):
        if self.ws is None:
            await self.open_socket()
        try:
            await self.ws.send(command)
            return await self.ws.recv()
        except Exception:
            self.open_socket()
            await self.ws.send(command)
            return await self.ws.recv()
