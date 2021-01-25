from os import name
import pymongo
import json
import sys
import logging
logging.basicConfig(level=logging.INFO)


class DB_Config:
    account_collection_name    = "#account"
    tableMeta_collection_name  = "#tableMeta"
    noneData_collection_names  = [account_collection_name, tableMeta_collection_name]
    tb_name                    = ''             # 
    db_host        = 'mongodb'      # 配置在/etc/hosts路径下的mongodb的服务地址（e.g.mongodb 10.0.0.98）
    # self.db_host = '10.0.0.98'    # 如果上面的配置不管用可以尝试手动配置连接地址
    # self.db_host = 'localhost'    # 本地默认连接地址（等同于127.0.0.1）
    db_port        = 27017          # 连接接口
    db_name                    = 'TableData'
    auth_db_name               = 'TableData'
    auth_usr                   = 'yefeng'
    auth_pass                  = 'yeFeng@123'

    def __init__(self, tb_name=None, db_host=None, db_port=None, db_name=None, collection_name=None):
        # If require custom Valus for config then pass via params
        if(tb_name is not None): self.tb_name = tb_name                 # 注意这里的文件名是带后缀的: 2020第一季度.xlsx     
        if(db_host is not None): self.db_host = db_host 
        if(db_port is not None): self.db_port = db_port
        if(db_name is not None): self.db_name = db_name
        if(collection_name is not None): self.collection_name = collection_name # 这里的文件名是不带后缀的: 2020第一季度
        return

class MongoDatabase:
    
    def __init__(self):
        return

    def start(self, host=None, port=None, name=None, clear=False, ptn=False):
        """
        打开与数据库的连接
        Parameter:
            host : MongoDB文档数据库所在 服务器IP地址
            port : MongoDB文档数据库所在 端口号
            name : MongoDB文档数据库中要打开的 数据库(Database)的 名字
            clear : 打开后是否清除数据库中原有的所有内容
            prn   : 是否print调试信息
        """

        # Use default configuration if not given
        default_config=DB_Config()
        if(host is None): host=default_config.db_host
        if(port is None): port=default_config.db_port
        if(name is None): name=default_config.db_name

        # create client instance and connect to database
        self.client = pymongo.MongoClient(host, port)
        self.database = self.client[default_config.auth_db_name]                       # 这里可以将admin替换成有数据库存账户信息的库
        self.database.authenticate(default_config.auth_usr, default_config.auth_pass)  # 登陆数据库认证 (等同于mongo shell 运行 use admin, db.auth(name,pwd))
        self.database = self.client[str(name)]                                         # 在认证后用client单独去关联

        if(clear):
            collection_names = self.database.list_collection_names()
            for collection_name in collection_names:
                collection_ = self.database[collection_name]
                collection_.drop()
                
        # if(ptn):
        #     print()
        #     print(f"\t* MongoDB:")
        #     print(f"\t* Client connecting to http://{host}:{port}/")
        #     print(f"\t* Clear DB mode: {'on' if clear else 'off'}")
        #     print()

        return 

    def close(self, clear=False, ptn=False):
        """
        关闭与数据库的连接
        """
        # close client instance
        if(clear):
            collection_names = self.database.list_collection_names()
            for collection_name in collection_names:
                collection_ = self.database[collection_name]
                collection_.drop()

        self.client.close()

        # if(ptn):
        #     print()
        #     print(f"\t* MongoDB:")
        #     print(f"\t* Stopped connection on http://{self.host}:{self.port}/")
        #     print(f"\t* Clear DB mode: {'on' if clear else 'off'}")
        #     print()

        return 

    def insert(self, collection, data, adapter=None, _id=None):
        """在已经打开的数据库中, 向特定的集合中(Collection), 插入特定id的文档(Document)
        Parameter
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
        """
        打开已经打开的数据库中的特定集合(Collection)
        """
        self.database.drop_collection(collection)
        return 

    def extract(self, collection, _id):
        """
        在已经打开的数据库中, 向特定的集合中(Collection), 获取特定id的文档(Document)
        Parameter
            collection : 数据库中集合的名字
            _id :        保存文档的_id (如果缺省那么就自动生成, 不推荐)
        """
        if(collection in self.database.list_collection_names()):  
            db_collection = self.database[collection]
            if(db_collection.count_documents({"_id":_id})!= 0):
                document = db_collection.find_one({"_id":_id})
                del document["_id"]
                return document
            else:
                raise(f"Document specified does not exist. (Document of _id={_id}")

        else:  
            raise(f"Collection specified does not exist. (Collection of _name={collection}")

        # if(collection.count_documents({"_id":_id}) == 0):
        # else: return collection.find_one({"_id":_id})

    def delete(self, collection, query):
        collection = self.database[collection]
        collection.delete_many(query)
        return

    def get_ids(self, collection):
        """
        获取已经打开的数据库中特定集合的所有文档的ID
        Parameter:
            collection : 数据库中集合的名字
        """
        if(collection in self.database.list_collection_names()):  
            cursor = self.database[collection].find({},{'_id':1}) 
            return [item['_id'] for item in cursor]
        else:  
            raise(f"Collection specified does not exist. (Collection of _name={collection}")

    def get_documents(self, collection, search_query=None, sort=(None,None)):
        """
        获取已经打开数据库中的特定集合中的符合查询条件的文档
        Parameter:
            collection : 数据库中集合的名字
            search_query : 字典类型的查询条件 例如{'_id':'abcdef123456', 'table_name':'demo_tableName'} 
        """

        # 如果没有给字典类型的Query, 那么默认返回集合全部的Document
        if(search_query is None):
            document_ids = self.get_ids(collection=collection)
            rtn_dict = {}
            for document_id in document_ids:
                document = self.extract(collection=collection, _id=document_id)
                rtn_dict[document_id] = document
            return rtn_dict

        # 否则根据查询条件找符合条件的Document
        else:
            if(collection in self.database.list_collection_names()):  
                db_collection = self.database[collection]
                if(db_collection.count_documents(search_query)!= 0):
                    if (sort is None) or (sort[0] is None) or (sort[1] is None):
                        document = db_collection.find(search_query)
                    else:
                        document = db_collection.find(search_query).sort(sort[0], sort[1])
                    # del document["_id"]
                    return document
                else:raise(f"Document specified does not exist. (Document of {str(search_query)}")
            else:raise(f"Collection specified does not exist. (Collection of _name={collection}")

    def list_tableData_collectionNames(self, exclude_collections=DB_Config.noneData_collection_names, database=None):
        """
        返回已打开数据库中跟表格数据有关集合的名字
        Parameter: 
            exclude_collections :   非表格数据集合名字, 将会被从列表中排出
            database :              如果不为None则重新连接 (TODO: 暂时还未实现该功能)
        """

        db = self.database
        names = db.list_collection_names()
        for collection_name in exclude_collections: # 去除非表格数据的集合
            if(collection_name in names): names.remove(collection_name) 
        return names

        # 高阶版本?
        # db = self.database
        # client = self.client
        # d = dict((db, [collection for collection in client[db].collection_names()])
        #      for db in client.database_names())
        # if(database is None): return json.dumps(d)
        # else: return d[database]
