from quart import Blueprint

from manager.balance_manager import balance_manager

api_balance_manager = Blueprint('api_balance_manager', __name__)

@api_balance_manager.route('/balance_manager/', methods=['GET'])
async def get_balance():
    response = await balance_manager.get_last_balance()
    print( response)
    return response
