import asyncio

from quart import Blueprint, jsonify, request, session

from manager.strategy_manager import StrategyManager, strategy_managers

api_strategy_manager = Blueprint('api_strategy_manager', __name__)

@api_strategy_manager.route('/strategy_manager/register/', methods=['GET','POST'])
async def register_strategy( ):
    try :
        args = request.args
        strategy_type=args.get('strategy_type')
        symbol=args.get('symbol')
        username=session['username']
        if username:
            if username in strategy_managers:
                strategy_manager = strategy_managers[username]
            else:
                strategy_manager = StrategyManager()
                strategy_managers[username] = strategy_manager
            await strategy_manager.register_strategy( strategy_type, symbol, username )
            resp = jsonify(success=True)
            resp.status_code = 200
            return resp
        else:
            resp = jsonify(success=False,msg="Not Logged In")
            resp.status_code = 500
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
        username = session['username']
        if username != None :
            if username in strategy_managers:
                strategy_manager = strategy_managers[username]
                await strategy_manager.unregister_strategy( strategy_type, symbol )
                resp = jsonify(success=True)
                resp.status_code = 200
                return resp
        resp = jsonify(success=False,message="Not Logged In")
        return resp
    except Exception as er:
        resp = jsonify(success=False,message=er)
        return resp