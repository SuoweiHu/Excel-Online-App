import pymongo
import json


class DB_Config:

    def __init__(self, tb_name=None, db_host=None, db_port=None, db_name=None, collection_name=None):
        # Default Values for config
        self.tb_name = ''           #'2020年二季度.xlsx'
        self.db_host = 'localhost'
        self.db_port = 27017
        self.db_name = "ExcelOnline"
        self.collection_name = ''   #'2020第二季度'  

        # Custom Valus for config
        if(tb_name is not None): self.tb_name = tb_name  # 注意这里的文件名是带后缀的: 2020第一季度.xlsx     
        if(db_host is not None): self.db_host = db_host 
        if(db_port is not None): self.db_port = db_port
        if(db_name is not None): self.db_name = db_name
        if(collection_name is not None): self.collection_name = collection_name # 里的文件名是不带后缀的: 2020第一季度

        return

class MongoDatabase:
    
    def __init__(self):
        return

    def start(self, host=None, port=None, name=None, clear=False, ptn=False):

        # Use default configuration if not given
        default_config=DB_Config()
        if(host is None): host=default_config.db_host
        if(port is None): port=default_config.db_port
        if(name is None): name=default_config.db_name

        # create client instance and connect to database
        self.client = pymongo.MongoClient(host, port)
        self.database = self.client[str(name)]

        if(clear):
            collection_names = self.database.list_collection_names()
            for collection_name in collection_names:
                collection_ = self.database[collection_name]
                collection_.drop()
                
        if(ptn):
            print()
            print(f"\t* MongoDB:")
            print(f"\t* Client connecting to http://{host}:{port}/")
            print(f"\t* Clear DB mode: {'on' if clear else 'off'}")
            print()

        return 

    def close(self, clear=False, ptn=False):
        # close client instance
        if(clear):
            collection_names = self.database.list_collection_names()
            for collection_name in collection_names:
                collection_ = self.database[collection_name]
                collection_.drop()

        self.client.close()

        if(ptn):
            print()
            print(f"\t* MongoDB:")
            print(f"\t* Stopped connection on http://{self.host}:{self.port}/")
            print(f"\t* Clear DB mode: {'on' if clear else 'off'}")
            print()

        return 

    def insert(self, collection, data, adapter=None, _id=None):
        """
        collection: MongoDB集合的名字
        data:       可以是dict, 当给出适配函数的时候, 也可以是excel, json等文件
        adapter:    可以把data转化成字典的函数 即 type(adapter(data)) == dict
        _id:        可缺省值, 保存文档的_id (如果缺省那么就自动生成, 不推荐)
        """
        if(adapter is not None):
            data = adapter(data)

        collection  = self.database[collection] 

        if(_id is None):
            # Insert data with random document _id
            collection.insert_one(collection)

        else:
            # Insert data with specified document _id (check exists?)
            data["_id"] = _id
            if(collection.count_documents({"_id":_id}) == 0): collection.insert_one(data)
            else: collection.update_one({"_id":_id}, {"$set":data})
            
        return

    def drop(self, collection):
        self.database.drop_collection(collection)
        return 

    def extract(self, collection, _id):
        collection  = self.database[collection] 
        if(collection.count_documents({"_id":_id}) == 0): raise(f"Document specified does not exist. \n Document of _id={_id}")
        else: return collection.find_one({"_id":_id})

    def list_collections(self, database=None):

        # Advanced Version
        # db = self.database
        # client = self.client
        # d = dict((db, [collection for collection in client[db].collection_names()])
        #      for db in client.database_names())
        # if(database is None): return json.dumps(d)
        # else: return d[database]

        # Simple version
        db = self.database
        names = db.list_collection_names()
        names.remove("User")
        return names
