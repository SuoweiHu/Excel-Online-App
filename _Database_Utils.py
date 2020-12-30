
from flask.config import Config
from _Database import MongoDatabase, DB_Config
from _TableData import TableData
from _Hash_Utils import hash_id

class Database_Utils:
    def count_allRows(config):
        """
        table name is filename with the .xlxs suffix
        for instance "2020年一季度.xlsx"
        """

        # Store to database
        db = MongoDatabase()
        db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
        temp_mongoLoad = db.extract(collection=config.collection_name,_id=hash_id(config.tb_name))
        db.close()

        # Store to custom type
        table = TableData(json=temp_mongoLoad)
        return len(table.operators)
        
    def count_completedRows(config):
        """
        table name is filename without the .xlxs suffix
        for instance "2020年一季度"
        """

        # Store to database
        db = MongoDatabase()
        db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
        temp_mongoLoad = db.extract(collection=config.collection_name,_id=hash_id(config.tb_name))
        db.close()

        # Store to custom type
        table = TableData(json=temp_mongoLoad)
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
    
    # ================================

    def get_tableTitles(tb_name):
        config = None
        if(tb_name is not None) and (config is None):
            config = DB_Config()
            config.collection_name = tb_name.split('.')[0]
            config.tb_name         = tb_name.split('.')[0] + ".xlsx"
        elif(config is not None) and (tb_name is None):pass
        else:raise("No input given (one of the tb_name, config must be filled)")

        db = MongoDatabase()
        db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
        temp_mongoLoad = db.extract(collection=config.collection_name,_id=hash_id(config.tb_name))
        db.close()

        table = TableData(json=temp_mongoLoad)
        titles = table.titles

        return titles

    def load_table(tb_name):
        config = None
        if(tb_name is not None) and (config is None):
            config = DB_Config()
            config.collection_name = tb_name.split('.')[0]
            config.tb_name         = tb_name.split('.')[0] + ".xlsx"
        elif(config is not None) and (tb_name is None):pass
        else:raise("No input given (one of the tb_name, config must be filled)")

        db = MongoDatabase()
        db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
        temp_mongoLoad = db.extract(collection=config.collection_name,_id=hash_id(config.tb_name))
        db.close()

        return temp_mongoLoad

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
        db.insert(collection=config.collection_name, data=data, _id=hash_id(config.tb_name))
        db.close()
        return

    # ================================

    def add_authorization(user_rows, col_name="账户", doc_id=0):
        # user_rows = 
        # {
        #   'admin' : {'password': 'admin', 'rows':[1,2,3,4,5]},
        #   'user1' : {'password': 'user1', 'rows':[1,2]},
        #   'user2' : {'password': 'user2', 'rows':[3,4]},
        #     ....  :      ....     ....      ....
        # }
        config = DB_Config()
        db = MongoDatabase()
        db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
        db.insert(collection=col_name, data=user_rows, _id=doc_id)
        db.close()

    def get_password(user_name, col_name="账户", doc_id=0):
        user_dict = Database_Utils.get_allAuthorization(col_name=col_name, doc_id=doc_id)
        if(user_name not in user_dict.keys()): return None
        return user_dict[user_name]['password']

    def get_allAuthorization(col_name="账户", doc_id=0):
        config = DB_Config()
        db = MongoDatabase()
        db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
        temp_userData = db.extract(collection=col_name, _id=doc_id)
        db.close()
        del temp_userData['_id']
        return temp_userData

    def get_authorizedRows(user_name, col_name="账户", doc_id=0):
        user_dict = Database_Utils.get_allAuthorization(col_name=col_name, doc_id=doc_id)
        if(user_name not in user_dict.keys()): return None
        return user_dict[user_name]['rows']


