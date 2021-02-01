from quart import Blueprint, jsonify, request, session

from trading_client.trading_client import TradingClient, trading_clients

api_trading_client = Blueprint('api_trading_client', __name__)

@api_trading_client.route('/login/', methods=['GET','POST'])
async def login( ):
    try :
        args = request.args
        username=args.get('username')
        password=args.get('password')

        session_trading_client = TradingClient()
        if username != None and password != None:
            log_response = await session_trading_client.login( username, password )
            if log_response['status'] == True:
                session['username']=username
                session['password']=password
                session['trading_client']=username
                trading_clients[username]=session_trading_client
                resp = jsonify(success=True)
                resp.status_code = 200
                return resp

    except Exception as er:
        resp = jsonify(success=False,message=str(er))
        return resp