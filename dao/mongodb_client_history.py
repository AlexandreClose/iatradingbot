import pymongo

from dao.mongodb_client import MongoDbClient


class MongoDbClientHistory(MongoDbClient):

    def __init__(self, symbol, *args, **kwargs ):
        super(MongoDbClientHistory, self).__init__("history","history_"+symbol,*args, **kwargs)
        self.client=pymongo.MongoClient("mongodb+srv://dbuser:Azerty123@cluster0.3wb5a.mongodb.net/")
        self.col.create_index([('Date', pymongo.ASCENDING)], unique=True, dropDups=True)