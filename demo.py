# Some built-int modules
import pprint

from modules._Database  import MongoDatabase, DB_Config
from modules._TableData import TableData
from modules._ExcelVisitor import ExcelVisitor
from modules._JsonVisitor  import JSON
# from modules._Redis import RedisCache
from modules._Database_Utils import Database_Utils
from modules._Hash_Utils import hash_id

# =============================================
# demo functions

# 2020.12.25
def demo_1():
    """
    Demo of following:
        - Using _ExcelVisitor to read from excel file
        - Using _TableData custom type to hold table sheet data 
        - Using _Database to save and read from mongo database
        - Using _Redis to save custom object to database (Failed)
    """
    config=DB_Config(tb_name="2020年二季度 copy.xlsx", db_host='localhost', db_port=27017, db_name="账户统计", collection_name="2020年二季度 copy")
    # config={
    #     "tb_name" : "2020年二季度.xlsx",
    #     "db_host" : 'localhost',
    #     "db_port" : 27017,
    #     "db_name" : "账户统计",
    #     "collection_name" : "2020第二季度",
    # }

    # Read from Excel file 
    tb_name     = config.tb_name
    excelReader = ExcelVisitor(ExcelVisitor.PATH+tb_name)
    titles      = excelReader.get_titles()
    info_table  = excelReader.get_infoTable()
    oper_table  = excelReader.get_operTable()

    # Store to custom class format 
    tableData = TableData(tb_name=tb_name, titles=titles, rows=info_table, operators=oper_table)
    tableDict = tableData.toJson()
    # print(tableDict)

    # # Try save variable into redis
    # r = RedisCache()
    # r.save(hash_id(config.tb_name), tableData)
    # temp_redisLoad = r.load(hash_id(config.tb_name))
    # JSON.save(temp_redisLoad, JSON.PATH+"temp.json")

    # Store to database
    db = MongoDatabase()
    db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
    db.insert(collection=config.collection_name, data=tableDict, _id=hash_id(config.tb_name))
    temp_mongoLoad = db.extract(collection=config.collection_name,_id=hash_id(config.tb_name))
    JSON.save(temp_mongoLoad, JSON.PATH+"temp.json")
    db.close()
    
    read_tableData = TableData(json=temp_mongoLoad)
    # print(read_tableData.rows)
    return

# 2020.12.28
# @app.route('/table')
def demo_2():
    """
    Demo of following:
        - Reading from .xlxs file and export to html
        - Flask app (when undesire to run, comment the route decorator)
    """
    config=DB_Config(tb_name="2020年二季度.xlsx")
    # config={
    #     "tb_name" : "2020年二季度.xlsx",
    # }

    # Read from Excel file 
    tb_name = config.tb_name
    excelReader = ExcelVisitor(ExcelVisitor.PATH+tb_name)
    titles      = excelReader.get_titles()
    info_table  = excelReader.get_infoTable()
    oper_table  = excelReader.get_operTable()

    # Convert the result to html format for printing
    tableData  = TableData(tb_name=tb_name, titles=titles, rows=info_table, operators=oper_table)
    jsonDict   = tableData.tableEdit_toJson(show_operator=True)
    htmlString = tableData.tableEdit_toHtml(json_dict=jsonDict,show_operator=True)

    # Return html string
    return htmlString

# 2020.12.29
def demo_3():
    """
    调整数据结构从
        {
            "name": "2020年二季度"
            "titles" : ["行号","项目号","子账户","账户名","分账户","账户名","受理人","金额"],
            "data"   : {
                "rows" :    [
                                ["733101","213123","A","XXXX","A1","XXXX","小S",None],
                                ["733121","123123","A","XXXX","A1","XXXX","小B","321"],
                                ["733131","123123","B","YYYY","B1","YYYY 1",None,"123"],
                                ["733141","123123","B","YYYY",None,None,None,"123"],
                                ["733151","1231231","B","YYYY","B3","YYYY 3","小B",None]
                            ],
                "operator" :[
                                {"name":"张三", "time":"2020.02.11 - 11:00:21"},
                                {"name":"李四", "time":"2020.02.11 - 11:00:21"},
                                {"name":"李四", "time":"2020.02.11 - 11:00:21"},
                                {"name":"王五", "time":"2020.02.11 - 11:00:21"},
                                {"name":"张三", "time":"2020.02.11 - 11:00:21"},
                            ]
        }
    到成为
        {
            "name" : "2020第一季度.xlxs",
            "data" : [
                {"行号" : 123123, “金额” : 111111, "名字" : 22222, "操作员": "胡所未", “操作时间”:“2020-02-02”}
                {"行号" : 123123, “金额” : 111111, "名字" : 22222, "操作员": "胡所未", “操作时间”:“2020-02-02”}
                {"行号" : 123123, “金额” : 111111, "名字" : 22222, "操作员": "胡所未", “操作时间”:“2020-02-02”}
                {"行号" : 123123, “金额” : 111111, "名字" : 22222, "操作员": "胡所未", “操作时间”:“2020-02-02”}
            ]
        }
    """
    config=DB_Config(tb_name="2020年二季度.xlsx", db_host='localhost', db_port=27017, db_name="账户统计", collection_name="2020年二季度")

    # Read from Excel file 
    tb_name     = config.tb_name
    excelReader = ExcelVisitor(ExcelVisitor.PATH+tb_name)
    titles      = excelReader.get_titles()
    info_table  = excelReader.get_infoTable()
    oper_table  = excelReader.get_operTable()

    # Store to custom class format 
    tableData = TableData(tb_name=tb_name, titles=titles, rows=info_table, operators=oper_table)
    tableDict = tableData.toJson()

    # CHECK READ  
    if(False): 
        pprint.pprint(tableData.tb_name, indent=4)
        print("="*30)
        pprint.pprint(tableData.titles, indent=4)
        print("="*30)
        pprint.pprint(tableData.rows, indent=4)
        print("="*30)
        pprint.pprint(tableData.operators, indent=4)
        print("="*30)
        pprint.pprint(tableDict, indent=4)

    # Store to database
    db = MongoDatabase()
    db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
    db.insert(collection=config.collection_name, data=tableDict, _id=hash_id(config.tb_name))
    temp_mongoLoad = db.extract(collection=config.collection_name,_id=hash_id(config.tb_name))
    # JSON.save(temp_mongoLoad, JSON.PATH+"temp.json")
    db.close()

    # Store to custom class format 
    tableData = TableData(json=temp_mongoLoad)
    tableDict = tableData.toJson()

    # CHECK READLoad
    if(False):
        pprint.pprint(tableData.tb_name, indent=4)
        print("="*30)
        pprint.pprint(tableData.titles, indent=4)
        print("="*30)
        pprint.pprint(tableData.rows, indent=4)
        print("="*30)
        pprint.pprint(tableData.operators, indent=4)
        print("="*30)
        pprint.pprint(tableDict, indent=4)
    
    # Complted rows
    c_comRow = Database_Utils.count_completedRows(config=config)
    c_allRow = Database_Utils.count_allRows(config=config)
    compltion_percentage = Database_Utils.get_completionPercentage(tb_name="2020年二季度")
    print("="*30)
    print(f"For the table of: {config.tb_name}")
    print(f"Number of completed rows: {c_comRow} / {c_allRow}")
    print(f"Completion percentages: {compltion_percentage}")
    print("="*30)

    return 

# 2020.12.30
def demo_4():
    # Stuff about account login 
    user_rows = {
        'admin' : {'password': 'admin', 'rows':[733101,733121,733131,733141,733151,733165,733177,733189,733201,733213,733225]},
        'user0' : {'password': 'user0', 'rows':[]},
        'user1' : {'password': 'user1', 'rows':[733101]},
        'user2' : {'password': 'user2', 'rows':[733121,733131]},
        'user3' : {'password': 'user3', 'rows':[733141,733151,733165]},
        'user4' : {'password': 'user4', 'rows':[]},
        'user5' : {'password': 'user5', 'rows':[]},
        'user6' : {'password': 'user6', 'rows':[]},
        'user7' : {'password': 'user7', 'rows':[]},
        'user8' : {'password': 'user8', 'rows':[]},
        'user9' : {'password': 'user9', 'rows':[]},
    }
    # Database_Utils.add_authorization(user_rows=user_rows)
    # temp_pass = Database_Utils.get_password(user_name='admin')
    # temp_auth = Database_Utils.get_authorizedRows(user_name='admin')

    # print(f"Password is {temp_pass}")
    # print(f"Allowed to changed rows{temp_auth}")
    return
