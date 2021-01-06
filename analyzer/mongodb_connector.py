import pymongo
from logging_conf import log

#base hebergée https://cloud.mongodb.com/ 

client = pymongo.MongoClient("mongodb+srv://dbHistory:Azerty123@cluster0.i5pmo.mongodb.net/<dbname>?retryWrites=true&w=majority")
db = client.test

dblist = client.list_database_names()
if not "historyDB" in dblist:
    mydb = client["historyDB"]
else:
    collection_name="EOS"
    collist = mydb.list_collection_names()
    if not collection_name in collist:
        mycol=mydb[collection_name]

class mongodb_connector():

    def __init__(self):
        self.mydb=None
        self.mycol=None
        self.client=None
    
    ##connection to MongoDB
    def connection(self):
        self.client = pymongo.MongoClient("mongodb+srv://dbHistory:Azerty123@cluster0.i5pmo.mongodb.net/<dbname>?retryWrites=true&w=majority")
        return db.test
    
    ##cretation of a DB
    def create_db(self,db_name):
        dblist = self.client.list_database_names()
        if db_name in dblist:
            log.debug("[MONGO] Database %s is already created", db_name)
        else:
            self.mydb = self.client["historyDB"]
    
    ## creation of collection in db
    def create_collection(self, collection_name):
        collist = self.mydb.list_collection_names()
        if collection_name in collist:
            log.debug("[MONGO] Collection %s is already created", collection_name)
        else:
            self.mycol=mydb[collection_name]
    
    ##check if db exists
    def check_db(self, db_name):
        dblist = self.client.list_database_names()
        if db_name in dblist:
            return(True)
        else:
            return (False)

    ##check if collection exists
    def check_collection(self,collection_name):
        collist = self.mydb.list_collection_names()
        if collection_name in collist:
            return (True)
        else:
            return (False)

    ##insert value in collection
    def collection_insert(self,mycol, data):
        x=mycol.insert_one(data)
        return (x.inserted_id)
    
    ##insert multiple value in collection
    def collection_insert_multiple(self, mycol=self.mycol, data):
        x = mycol.insert_many(data)
        return(x.inserted_ids)

    #find all in collection
    def find_all(self, mycol=self.mycol):
        data_list=[]
        for x in mycol.find():
            data_list.append(x)
        return data_list

    #find object in collection
    def find_all(self, mycol=self.mycol, data):
        data_list=[]
        mydoc=mycol.find(data)
        for x in mydoc:
            data_list.append(x)
        return data_list


    ##getter
    def get_db(self):
        return self._mydb
    
    ##getter
    def get_collection(self):
        return self._mycol

    ##setter
    def set_db(self, db_name):
        self._mydb=db_name
    
    ##setter
    def set_collection(self, collection_name):
        self._mycol=collection_name

    





    
