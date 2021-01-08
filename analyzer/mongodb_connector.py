import pymongo


#base hebergée https://cloud.mongodb.com/ 

#compte
#user : ctatangelo@silicom.fr
#password : Azerty#456

#db user
#user : dbuser
#password : Azerty123

class mongodb_connector():

    def __init__(self):
        self.mydb=None
        self.mycol=None
        self.client=None
    
    ##connection to MongoDB
    def connect(self):
        self.client = pymongo.MongoClient("mongodb+srv://dbuser:Azerty123@cluster0.3wb5a.mongodb.net/")

    ##cretation of a DB
    def create_db(self,db_name):
        #print (self.client)
        self.mydb = self.client[db_name]
        print(self.client.list_database_names())
        dblist = self.client.list_database_names()
        if db_name in dblist:
            print('hello')
        else:
            self.mydb = self.client[db_name]

    ## creation of collection in db
    def create_collection(self, collection_name):
        collist = self.mydb.list_collection_names()
        if collection_name in collist:
            print('loh')
            #log.debug("[MONGO] Collection %s is already created", collection_name)
        else:
            self.mycol=self.mydb[collection_name]
    
    ##check if db exists
    def check_db(self, db_name):
        dblist = self.client.list_database_names()
        if db_name in dblist:
            return(True)
        else:
            return (False)

    ##check if collection exists
    def check_collection(self,collection_name):
        collist = self.mycol.list_collection_names()
        if collection_name in collist:
            return (True)
        else:
            return (False)

    ##insert value in collection
    def collection_insert(self, data, mycol=None):
        if mycol==None:
            mycol=self.mycol
        x=mycol.insert_one(data)
        return (x.inserted_id)
    
    ##insert multiple value in collection
    def collection_insert_multiple(self, data, mycol=None):
        if mycol==None:
            mycol=self.mycol
        x = mycol.insert_many(data, ordered=False)
        return(x.inserted_ids)

    #find all in collection
    def find_all(self, mycol=None):
        if mycol==None:
            mycol=self.mycol
        data_list=[]
        for x in mycol.find():
            data_list.append(x)
        return data_list

    #find object in collection
    def find_data(self, data, mycol=None):
        if mycol==None:
            mycol=self.mycol
        data_list=[]
        mydoc=mycol.find(data)
        for x in mydoc:
            data_list.append(x)
        return data_list

    ##sort data ascending  = 1, descending=2
    def sortdata(self,data,standard,mycol=None):
        if standard==1:
            sort=1
        if standard==2:
            sort=-1
        if mycol==None:
            mycol=self.mycol
        data_list=[]
        mydoc=mycol.find().sort(data,sort)
        for x in mydoc:
            data_list.append(x)
        return data_list

    ##getter
    def get_db(self):
        return self.mydb
    
    ##getter
    def get_collection(self):
        return self.mycol

    ##setter
    def set_db(self, db_name):
        self.mydb=self.client[db_name]
    
    ##setter
    def set_collection(self, collection_name):
        self.mycol=self.mydb[collection_name]

    





    
