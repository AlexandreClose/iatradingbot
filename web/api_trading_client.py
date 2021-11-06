import logging

import flask_login
from logging_conf import log
from flask_login import login_user
from quart import Blueprint, jsonify, request, session

from manager.user_manager import user_manager
from trading_client.trading_client import TradingClient, trading_clients
from web.user import User

api_trading_client = Blueprint('api_trading_client', __name__)

@api_trading_client.route('/login/', methods=['GET','POST'])
async def login( ):
    try :
        args = request.args
        username=args.get('username')
        password=args.get('password')
        user = User()
        user.id = username

        if username in trading_clients:
            client = trading_clients[username]
            # check password
            if password == client.password:
                 # check login
                isLoggedIn = await client.ping()
                if not isLoggedIn:
                    response = await client.login( username, password, True )
                    if not response["status"]:
                        raise Exception('Unable to process log in')
            else:
                isLoggedIn = await client.ping()
                if isLoggedIn:
                    raise Exception('Invalid password')
                else:
                    client = TradingClient()
                    response = await client.login(username, password, True)
                    if response["status"]:
                        #Register the user with new pass
                        trading_clients[username]=client
                        user_manager.deleteOne( {"username" : username} )
                        user_manager.register_user({
                            "username": username,
                            "password": password
                        })
        else:
            client = TradingClient()
            response = await client.login(username, password, True)
            if response["status"]:
                # Register the user with new pass
                trading_clients[username] = client
                try:
                    user_manager.register_user({
                        "username": username,
                        "password": password
                    })
                except:
                    log.info( "User %s already exists in database", username)
            else:
                raise Exception('Unable to process log in')

        #log flask user
        login_user(user)
        resp = jsonify(success=True, message="Login successful")
        resp.status_code = 200
        return resp
    except Exception as er:
        resp = jsonify(success=False,message=str(er))
        resp.status_code = 403
        return resp