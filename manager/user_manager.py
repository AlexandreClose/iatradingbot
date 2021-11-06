from quart import session

from dao.dao_user import MongoDbClientUser
from trading_client.trading_client import TradingClient, trading_clients
from utils.singleton import Singleton

# not a singleton. Depending on session
class UserManager:

    def __init__(self ):
        self.userDao : MongoDbClientUser = MongoDbClientUser()

    def get_all_users(self ):
        return self.userDao.find()

    def register_user(self, user ):
        return self.userDao.insert( user )

    def deleteOne(self, conditions):
        return self.userDao.deleteOne( conditions)

    def get_user_by_username(self, username):
        return self.userDao.find( {"username": username})

user_manager = UserManager( )