
import sys
import pprint
from flask import config
from flask.config import Config
from pymongo.mongo_client import MongoClient
from ._Database import MongoDatabase, DB_Config
from ._TableData import TableData
from ._Hash_Utils import hash_id

account_collection_name = DB_Config.account_collection_name

class Database_Utils:
    # ================================

    def list_collections():
        db = MongoDatabase()
        db.start()
        collection_names = db.list_collections()
        db.close()
        return collection_names

    def count_allRows(config):
        """
        table name is filename with the .xlxs suffix
        for instance "2020年一季度.xlsx"
        """

        table_name =config.collection_name

        # Store to database
        db = MongoDatabase()
        db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
        temp_mongoLoad = db.get_documents(collection=table_name)
        db.close()

        # Store to custom type
        table = TableData(json=temp_mongoLoad, tb_name=table_name)
        return len(table.operators)
        
    def count_completedRows(config):
        """
        table name is filename without the .xlxs suffix
        for instance "2020年一季度"
        """

        # Store to database
        db = MongoDatabase()
        db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
        table_name = config.collection_name
        temp_mongoLoad = db.get_documents(collection=table_name)
        db.close()



        # Store to custom type
        table = TableData(json=temp_mongoLoad, tb_name=table_name)
        operators = table.operators

        count = 0
        for operator in operators:
            if(operator[0] is not None) and (operator[1] is not None):
                count += 1

        return count 

    def get_completionPercentage(tb_name=None, config=None):
        if(tb_name is not None) and (config is None):
            config = DB_Config()
            config.collection_name = tb_name.split('.')[0]
            config.tb_name         = tb_name.split('.')[0] + ".xlsx"
        elif(config is not None) and (tb_name is None):
            # config = config
            pass
        else:
            raise("No input given (one of the tb_name, config must be filled)")

        c_comRow = Database_Utils.count_completedRows(config=config)
        c_allRow = Database_Utils.count_allRows(config=config)

        return round(c_comRow/c_allRow * 100, 1)
    
    def check_rowCompleted(config, authorized_banknos, key="行号"):
        table_name = config.collection_name
        db = MongoDatabase()
        db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
        temp_mongoLoad = db.get_documents(collection=table_name)
        db.close()
        for bankno in authorized_banknos:
            bankno = str(bankno)
            table = TableData(json=temp_mongoLoad, tb_name=table_name)
            bankno_index = table.titles.index(key)
            for i in range (len(table.rows)):
                row = table.rows[i]
                if(row[bankno_index] == bankno):
                    if(table.operators[i][0] is None):
                        return False
        return True

    # ================================

    def upload_table(name, data):
        config= DB_Config(tb_name=name, collection_name=name.split('.')[0])
        db = MongoDatabase()
        db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
        for row in data.items():
            db.insert(collection=name, data=row[1], _id=row[0])
        db.close()
        return

    def get_tableTitles(tb_name):
        # config = None
        # if(tb_name is not None) and (config is None):
        #     config = DB_Config()
        #     config.collection_name = tb_name.split('.')[0]
        #     config.tb_name         = tb_name.split('.')[0] + ".xlsx"
        # elif(config is not None) and (tb_name is None):pass
        # else:raise("No input given (one of the tb_name, config must be filled)")

        table_name = tb_name
        config = DB_Config(collection_name=tb_name)
        db = MongoDatabase()
        db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
        temp_mongoLoad = db.get_documents(collection=table_name)
        db.close()

        table = TableData(json=temp_mongoLoad, tb_name=table_name)
        titles = table.titles
        return titles

    def load_table(tb_name):
        # if(tb_name is not None) and (config is None):
        #     config = DB_Config()
        #     config.collection_name = tb_name.split('.')[0]
        #     config.tb_name         = tb_name.split('.')[0] + ".xlsx"
        # elif(config is not None) and (tb_name is None):pass
        # else:raise("No input given (one of the tb_name, config must be filled)")

        table_name = tb_name
        config = DB_Config()
        db = MongoDatabase()
        db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
        temp_mongoLoad = db.get_documents(collection=table_name)
        db.close()

        table = TableData(json=temp_mongoLoad, tb_name=table_name)
        return table

    def save_table(tb_name,data):
        config = None
        if(tb_name is not None) and (config is None):
            config = DB_Config()
            config.collection_name = tb_name.split('.')[0]
            config.tb_name         = tb_name.split('.')[0] + ".xlsx"
        elif(config is not None) and (tb_name is None):pass
        else:raise("No input given (one of the tb_name, config must be filled)")

        db = MongoDatabase()
        db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
        # db.drop(collection=config.collection_name)
        for row in data.items():
            db.insert(collection=tb_name, data=row[1], _id=row[0])
        db.close()
        return 

    # ================================

    def get_user(name):
        config = DB_Config()
        db = MongoDatabase()
        db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
        _id = hash_id(name)
        user_dict = db.database[account_collection_name].find_one({'_id':_id})
        db.close()
        return user_dict

    def add_user(name, password, rows, privilege='generic'):
        config = DB_Config()
        db = MongoDatabase()
        db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)

        # 生成用户唯一的ID
        _id      = hash_id(name)
        hash_password = hash_id(password)
        usr_dict = {'name':name, 'password':hash_password, 'privilege':privilege, 'rows':rows}

        # 如果已经存在用户则抛出错误 (可以后面改) 否则添加用户字典数据
        if(db.database[account_collection_name].count_documents({'_id':_id}) == 1): 
            db.insert(collection=account_collection_name, data=usr_dict, _id=_id)
            # raise(f"The account adding already exists : _id={_id}")
        else: db.insert(collection=account_collection_name, data=usr_dict, _id=_id)

        db.close()
        return

    def del_user(name, password):
        config = DB_Config()
        db = MongoDatabase()
        db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)

        # 生成用户唯一的ID
        _id      = hash_id(name)
        hash_password = hash_id(password)

        if(db.database[account_collection_name].count_documents({'_id':_id}) == 0): 
            db.close()
            return
            # raise(f"Your deleting account dont exist")
        else: 
            if(Database_Utils.check_password(name, password)):
                col = db.database[account_collection_name]
                col.delete_one({'_id' : hash_id(name)})
                db.close()
                return 

        db.close()
        return

    def check_password(name, password):
        """
        返回true如果密码和数据库中的hash匹配
        """
        if((Database_Utils.get_user(name)) is None): return False
        return (Database_Utils.get_user(name))['password'] == hash_id(password)

    def check_admin(name):
        """
        返回true如果用户的privilege字段为admin
        """
        return (Database_Utils.get_user(name))['privilege'] == 'admin'
        
    def get_rows(name):
        """
        返回用户有权限访问的行
        """
        return (Database_Utils.get_user(name)['rows'])

    # ================================

    def get_table_row(table_name, row_id):
        """
        table_name: 表格名, 数据库中对应一个集合
        row_id:     行uuid, 数据库中对应刚刚集合中的一个文件
        return:     整个文件 (包含其id, 需自行去除)
        """

        db_config = DB_Config()
        db = MongoDatabase()
        db.start(host=db_config.db_host, port=db_config.db_port, name=db_config.db_name,clear=False)
        rtn = db.database[table_name].find_one({'_id':row_id})
        db.close()
        return rtn

    def set_table_row(table_name, row_id, data):
        """
        table_name: 表格名, 数据库中对应一个集合
        row_id:     行uuid, 数据库中对应刚刚集合中的一个文件
        return:     整个文件 (包含其id, 需自行去除)
        """
        db_config = DB_Config()
        db = MongoDatabase()
        db.start(host=db_config.db_host, port=db_config.db_port, name=db_config.db_name,clear=False)
        # db.database[table_name].delete_one({'_id':row_id})
        # db.database[table_name].insert_one(data)
        db.database[table_name].update_one({'_id':row_id}, {'$set': data})
        db.close()
        return 


        



