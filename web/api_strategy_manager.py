from quart import Blueprint, jsonify

from manager.symbol_manager import symbol_manager

api_symbol_manager = Blueprint('api_symbol_manager', __name__)

@api_symbol_manager.route('/symbol_manager/register/<symbol>', methods=['GET','POST'])
async def register_symbol( symbol ):
    try :
        await symbol_manager.register_symbol( symbol )
        resp = jsonify(success=True)
        resp.status_code = 200
        return resp
    except Exception as er:
        resp = jsonify(success=False,message=er)
        return resp

@api_symbol_manager.route('/symbol_manager/unregister/<symbol>', methods=['GET','POST'])
async def unregister_symbol( symbol ):
    try :
        await symbol_manager.unregister_symbol( symbol )
        resp = jsonify(success=True)
        resp.status_code = 200
        return resp
    except Exception as er:
        resp = jsonify(success=False,message=er)
        return resp