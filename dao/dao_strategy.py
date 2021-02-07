import pymongo

from dao.dao_base_client import MongoDbBaseClient

class DaoStrategy(MongoDbBaseClient):

    def __init__(self, *args, **kwargs ):
        super(DaoStrategy, self).__init__("management", "strategy", *args, **kwargs)
        self.client=pymongo.MongoClient("mongodb+srv://dbuser:Azerty123@cluster0.3wb5a.mongodb.net/")

strategy_dao :DaoStrategy = DaoStrategy()
