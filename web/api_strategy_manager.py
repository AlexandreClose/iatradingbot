from quart import Blueprint, jsonify, request

from manager.strategy_manager import strategy_manager

api_strategy_manager = Blueprint('api_strategy_manager', __name__)

@api_strategy_manager.route('/strategy_manager/register/', methods=['GET','POST'])
async def register_strategy( ):
    try :
        args = request.args
        strategy_type=args.get('strategy_type')
        symbol=args.get('symbol')
        await strategy_manager.register_strategy( strategy_type, symbol )
        resp = jsonify(success=True)
        resp.status_code = 200
        return resp
    except Exception as er:
        resp = jsonify(success=False,message=str(er))
        return resp

@api_strategy_manager.route('/strategy_manager/unregister/', methods=['GET','POST'])
async def unregister_strategy( ):
    try :
        args = request.args
        strategy_type=args.get('strategy_type')
        symbol=args.get('symbol')
        await strategy_manager.unregister_strategy( strategy_type, symbol )
        resp = jsonify(success=True)
        resp.status_code = 200
        return resp
    except Exception as er:
        resp = jsonify(success=False,message=er)
        return resp