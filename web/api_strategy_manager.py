import asyncio

import flask_login
from flask_login import login_required
from quart import Blueprint, jsonify, request, session

from manager.strategy_manager import StrategyManager, strategy_managers

api_strategy_manager = Blueprint('api_strategy_manager', __name__)

@api_strategy_manager.route('/strategy_manager/register/', methods=['GET','POST'])
@login_required
async def register_strategy( ):
    try :
        args = request.args
        strategy_type=args.get('strategy_type')
        symbol=args.get('symbol')
        username=flask_login.current_user.id
        if username:
            if not username in strategy_managers:
                strategy_managers[username]=StrategyManager()
            await strategy_managers[username].register_strategy( strategy_type, symbol, None, username, optimize=False )
            # register
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
@login_required
async def unregister_strategy( ):
    try :
        args = request.args
        strategy_type=args.get('strategy_type')
        symbol=args.get('symbol')
        username = username=flask_login.current_user.id
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

@api_strategy_manager.route('/strategy_manager/', methods=['GET'])
@login_required
async def get_strategies( ):
    try :
        args = request.args
        strategy_type=args.get('strategy_type')
        symbol=args.get('symbol')
        username=flask_login.current_user.id
        if username != None :
            if username in strategy_managers:
                strategy_manager : StrategyManager = strategy_managers[username]
                strategies = await strategy_managers[username].get_registered_strategies ( )
                resp = jsonify(strategies)
                resp.status_code = 200
                return resp
        resp = jsonify(success=False,message="Not Logged In")
        return resp
    except Exception as er:
        resp = jsonify(success=False,message=er)
        return resp