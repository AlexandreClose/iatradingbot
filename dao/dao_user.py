import pymongo

from dao.dao_base_client import MongoDbBaseClient


class MongoDbClientUser(MongoDbBaseClient):

    def __init__(self, *args, **kwargs ):
        super(MongoDbClientUser, self).__init__("management","user",*args, **kwargs)
        self.col.create_index([('username', pymongo.ASCENDING)], unique=True, dropDups=True)
user_dao :MongoDbClientUser = MongoDbClientUser()