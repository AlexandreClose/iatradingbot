from trading_client.trading_client import trading_client, TradingClient
from utils.singleton import Singleton


@Singleton
class BalanceManager:

    def __init__(self ):
        self.client : TradingClient = trading_client

    async def get_last_balance(self):
        return await self.client.get_last_updated_balance()

balance_manager = BalanceManager.instance()