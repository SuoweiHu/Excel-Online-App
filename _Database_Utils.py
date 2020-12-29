
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

