from quart import Blueprint, session, jsonify

from manager.balance_manager import balance_managers, BalanceManager

api_balance_manager = Blueprint('api_balance_manager', __name__)

@api_balance_manager.route('/balance_manager/', methods=['GET'])
async def get_balance():
    print (session)
    username=session['username']

    if username:
        if username in balance_managers:
            balance_manager = balance_managers[username]
        else:
            balance_manager = BalanceManager()
        response = await balance_manager.get_last_balance()
        resp = jsonify(response)
        resp.status_code = 200
        return resp
    else:
        resp = jsonify(success=False,msg="Not Logged In")
        resp.status_code = 500
        return resp
