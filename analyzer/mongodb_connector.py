import pymongo

client = pymongo.MongoClient("mongodb+srv://dbHistory:Azerty123@cluster0.i5pmo.mongodb.net/<dbname>?retryWrites=true&w=majority")
db = client.test
