from platform import platform
import pymongo


class MongoVisitor:
    
    def __init__(self):
        return

    def start(self, host, port, name, clear=False, ptn=False):
        # create client instance and connect to database
        self.client = pymongo.MongoClient(host, port)
        self.database = self.client[name]

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

    def extract(self, collection, _id):
        collection  = self.database[collection] 
        if(collection.count_documents({"_id":_id}) == 0): raise(f"Document specified does not exist. \n Document of _id={_id}")
        else: return collection.find_one({"_id":_id})