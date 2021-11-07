import json

from quart import session

from trading_client.trading_client import TradingClient, trading_clients
from logging_conf import log

class BalanceManager:

    def __init__(self, username='admin' ):
        self.client : TradingClient = trading_clients[username]
        self.username = username

    async def get_last_balance(self):
        last_balance =  await self.client.get_last_updated_balance()
        if not last_balance:
            last_balance = await self.client.get_last_updated_balance_no_stream()
        log.info( "[BALANCE] Fetch last balance for user %s. Value : %s", self.username, json.dumps( last_balance ) )
        return last_balance

admin_balance_manager = BalanceManager( )
balance_managers={}
balance_managers['admin']=admin_balance_manager