from quart import Blueprint

from manager.balance_manager import balance_manager

api_manager = Blueprint('api_manager', __name__)

@api_manager.route('/balance', methods=['GET'])
async def get_balance():
    response = await balance_manager.get_last_balance()
    print( response)
    return response
