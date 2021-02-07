import pymongo

from dao.dao_base_client import MongoDbBaseClient


class MongoDbClientUser(MongoDbBaseClient):

    def __init__(self, *args, **kwargs ):
        super(MongoDbClientUser, self).__init__("management","user",*args, **kwargs)
        self.client=pymongo.MongoClient("mongodb+srv://dbuser:Azerty123@cluster0.3wb5a.mongodb.net/")

user_dao :MongoDbClientUser = MongoDbClientUser()