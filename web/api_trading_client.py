import flask_login
from flask_login import login_user
from quart import Blueprint, jsonify, request, session

from manager.user_manager import user_manager
from trading_client.trading_client import TradingClient, trading_clients
from web.user import User

api_trading_client = Blueprint('api_trading_client', __name__)

@api_trading_client.route('/login/', methods=['GET','POST'])
async def login( ):
    try :
        args = request.args
        username=args.get('username')
        password=args.get('password')
        user = User()
        user.id = username

        user_registered = user_manager.get_user_by_username( username )[0]
        if not user_registered:
            # try login with trading client
            trading_client = TradingClient()
            login_response = await trading_client.login( username, password )
            if login_response['status'] == True:
                user_manager.register_user( {
                    "username":username,
                    "password":password
                })
                trading_clients[username]=trading_client
            else:
                return
        else:
            if not username in trading_clients:
                trading_client = TradingClient()
                login_response = await trading_client.login( username, password )
                if login_response['status'] == True:
                    trading_clients[username]=trading_client
        login_user(user)
        return 'test'

    except Exception as er:
        resp = jsonify(success=False,message=str(er))
        return resp