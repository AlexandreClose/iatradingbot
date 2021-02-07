import flask_login
from flask_login import login_required
from quart import Blueprint, session, jsonify

from manager.balance_manager import balance_managers, BalanceManager
from trading_client.trading_client import trading_clients

api_balance_manager = Blueprint('api_balance_manager', __name__)

@api_balance_manager.route('/balance_manager/', methods=['GET'])
@login_required
async def get_balance():
    username=flask_login.current_user.id

    if username and username in trading_clients:
        if username in balance_managers:
            balance_manager = balance_managers[username]
        else:
            balance_manager = BalanceManager( username )
            balance_managers[username]=balance_manager
        response = await balance_managers[username].get_last_balance()
        resp = jsonify(response)
        resp.status_code = 200
        return resp
    else:
        resp = jsonify(success=False,msg="Not Logged In")
        resp.status_code = 500
        return resp
