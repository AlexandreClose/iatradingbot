import asyncio
import json

import flask_login
from flask_login import login_required
from quart import Blueprint, jsonify, request, session, app

from manager.strategy_manager import StrategyManager, strategy_managers

api_strategy_manager = Blueprint('api_strategy_manager', __name__)

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'reprJSON'):
            return obj.reprJSON()
        else:
            return json.JSONEncoder.default(self, obj)

@api_strategy_manager.route('/strategy_manager/register/', methods=['GET','POST'])
@login_required
async def register_strategy( ):
    try :
        args = request.args
        strategy_type=args.get('strategy_type')
        symbol=args.get('symbol')
        optimize=args.get('optimize')=="true"
        n_currencies=float(args.get('n_currencies'))
        username=flask_login.current_user.id
        if username:
            if not username in strategy_managers:
                strategy_managers[username]=StrategyManager()
            strategy = await strategy_managers[username].register_strategy( strategy_type, symbol, n_currencies, username, optimize=optimize )
            data = json.dumps(strategy, cls=ComplexEncoder)
            data = json.loads(data)
            resp = jsonify(success=True, strategy = data)
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
        username=flask_login.current_user.id
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

@api_strategy_manager.route('/strategy_manager/unregister_by_id/', methods=['GET','POST'])
@login_required
async def unregister_strategy_by_id( ):
    try :
        args = request.args
        id=args.get('id')
        username=flask_login.current_user.id
        if username != None :
            if username in strategy_managers:
                strategy_manager = strategy_managers[username]
                await strategy_manager.unregister_strategy_by_id( id )
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
        username=flask_login.current_user.id
        if username != None :
            if username in strategy_managers:
                strategies = await strategy_managers[username].get_registered_strategies ( )
                data = json.dumps(strategies, cls=ComplexEncoder)
                data = json.loads( data )
                resp = jsonify( data)
                resp.status_code = 200
                return resp
            else:
                resp =  jsonify([])
                resp.status_code = 200
                return resp
        else:
            resp = jsonify(success=False,message="Not Logged In")
            return resp
    except Exception as er:
        resp = jsonify(success=False,message=er)
        return resp