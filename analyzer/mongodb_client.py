import enum

import pymongo
from logging_conf import log


#base hebergée https://cloud.mongodb.com/ 

#compte
#user : ctatangelo@silicom.fr
#password : Azerty#456

#db user
#user : dbuser
#password : Azerty123
from pymongo.errors import BulkWriteError


class SORT_TYPE(enum.Enum):
    ASCENDING = 1
    DESCENDING = -1

class MongoDbClient():

    def __init__(self, db_name, col_name):
        self.client=pymongo.MongoClient("mongodb+srv://dbuser:Azerty123@cluster0.3wb5a.mongodb.net/")
        self.db=self.client[db_name]
        self.col=self.db[col_name]

    def insert(self, data ):
        x=self.col.insert_one(data)
        return (x.inserted_id)

    def insert_multiple(self, bulk_data):
        try:
            x = self.col.insert_many(bulk_data, ordered=False)
            return (x.inserted_ids)
        except BulkWriteError as err:
            log.error( err )

    def find(self, data=None, sort=None ):
        if data is not None:
            datas = self.col.find( data )
        else :
            datas = self.col.find()
        if sort is not None:
            datas = datas.sort( sort )
        return datas