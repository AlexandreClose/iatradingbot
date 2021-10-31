from conf.xtb_admin_account import xtb_admin_account_password, xtb_admin_account_id
from dao.dao_strategy import strategy_dao
from dao.dao_user import user_dao
from manager.strategy_manager import StrategyManager, strategy_managers
from trading_client.trading_client import trading_clients, TradingClient, admin_trading_client
from utils.singleton import Singleton


@Singleton
class AppReloadService:
    async def reload_app_context(self):

        # load ang log the admin trading client
        await admin_trading_client.login( xtb_admin_account_id, xtb_admin_account_password )

        # load users
        users = user_dao.find()

        #run all the trading client
        for user in users:
            trading_clients[user["username"]]=TradingClient()
            await trading_clients[user["username"]].login(user["username"],user["password"] )

        # load strategies
        strategies = strategy_dao.find()
        for strategy in strategies:
            username = strategy["username"]
            if username not in strategy_managers:
                strategy_manager = StrategyManager()
                strategy_managers[username] = strategy_manager
            await strategy_managers[username].register_strategy(
                strategy_type=strategy["strategy_type"],
                symbol=strategy["symbol"],
                n_currency=strategy["n_currency"],
                username=strategy["username"],
                params_opti = strategy["params_opti"],
                from_dao = True)

app_reload_service = AppReloadService.instance()
app_reload_service : AppReloadService