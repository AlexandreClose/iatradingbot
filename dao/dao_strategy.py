import pymongo

from dao.dao_base_client import MongoDbBaseClient

class DaoStrategy(MongoDbBaseClient):

    def __init__(self, *args, **kwargs ):
        super(DaoStrategy, self).__init__("management", "strategy", *args, **kwargs)

strategy_dao :DaoStrategy = DaoStrategy()
