import flask_login
from quart import Quart
from quart_cors import cors

from manager.user_manager import user_manager
from web.api_balance_manager import api_balance_manager
from web.api_strategy_manager import api_strategy_manager
from web.api_symbol_manager import api_symbol_manager
from web.api_trading_client import api_trading_client
from web.user import User

log_manager = flask_login.LoginManager()

@log_manager.user_loader
def load_user_by_name(username):
    user = User()
    user.id = username
    return user

@log_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'

def create_app( ):
    app = Quart("name")
    app.secret_key = "sg,vdnfknkndsknerngsvqdfjgdsnqjfvn djsg j"
    log_manager.init_app(app)
    app.register_blueprint(api_balance_manager)
    app.register_blueprint(api_symbol_manager)
    app.register_blueprint(api_strategy_manager)
    app.register_blueprint(api_trading_client)
    app = cors(app, allow_origin="http://localhost:8080", allow_credentials=True)
    return app
