# Some built-int modules
import json
import os
import sys
import pprint
import datetime
import random

# Custom modules
from _Database  import MongoDatabase, DB_Config
from _TableData import TableData
from _ExcelVisitor import ExcelVisitor
from _JsonVisitor  import JSON
from _Redis import RedisCache
from _Database_Utils import Database_Utils
from _Hash_Utils import hash_id

# Imported libraries
from pymongo.periodic_executor import _on_executor_deleted
from werkzeug import utils
from json2html import json2html
from flask      import Flask, config, render_template, flash, make_response, send_from_directory, redirect, url_for, session, request

# =============================================
# Flask Application's instance

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SAJHDKSAKJDHKJASHKJDKASDD'  
# app.config['MAXs_CONTENT_LENGTH'] = 5 * 1024 * 1024

# =============================================
# helper functions

def gen_dateTime_str():
    now = datetime.datetime.now()

    # Day - transformation
    day = now.date()
    # day_str = day.__str__
    day_str = day.__format__('%y/%m/%d')

    # Time - transofmation
    time = now.time()
    # time_str = time.__str__
    time_str = time.strftime('%H:%M:%S')

    return f"{day_str} {time_str}"

def gen_operInfo_tup():
    # Add form info into string 
    now = datetime.datetime.now()
    day = now.date()
    time = now.time()
    day_str = day.__format__('%Y/%m/%d')
    time_str = time.strftime('%H:%M:%S')
    datetime_str = day_str+ " " + time_str
    # print(datetime_str)
    operator_str = session["operator_name"]
    return (operator_str, datetime_str)

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


# =============================================
# flask router: main page

@app.route('/', methods=["POST","GET"])
def initialize():
    session['login_state'] = False
    session['operator']    = None
    session['operator_name'] = None
    session['previous_page'] = None
    return redirect(url_for('index'))

@app.route('/redirect', methods=["POST","GET"])
def redirect_to_index():
    if(session['previous_page'] is None):
        return redirect(url_for('index'))
    else:
        prev_page = session['previous_page']
        session['previous_page'] = None
        return redirect(prev_page)

@app.route('/index')
def index():
    if(not session['login_state']==True):
        fileUpload_section = "请登录, 以访问数据库 ... ..."
        insert_section = "请登录, 以访问数据库 ... ..."
        # delete_section = "请登录, 以访问数据库 ... ..."
        login_section  = """
            登陆以获得更多权限<br><br>
            <form action="/login" method="post">
                账户名:      
                <input type="text" name="operator_name" id=""><br>
                &nbsp;密码:&nbsp;&nbsp;&nbsp; 
                <input type="password" name="operator_pass" id=""><br>
                <br>
                <input type="submit" value="提交">
            </form>
            """
    else:
        fileUpload_section = """
            <form action="/file" method="post" enctype="multipart/form-data">
                <input type="file" name="stuff_file"  id=""><br><br>
                <input type="submit" value="--- 上传 ---">
            </form>
            """
        insert_section = """
            <!---查看所有表单-->
            <form action="/table/all" method="post">
                <input type="submit" value="更改/查看 已有表单">
            </form>
            <br>
            """
        # Add operator info 
        operator_infos = gen_operInfo_tup()
        operator_name  = operator_infos[0]
        operator_date  = operator_infos[1].split(' ')[0]
        operator_time  = operator_infos[1].split(' ')[1]

        # insert_section = """
            # <!---查看特定表单-->
            # <form action="/table" method="post">
            #     更改/查看特定表单:
            #     <select name="table_name" id="table_name">
            #         <option value="2020年一季度.xlsx">2020年一季度.xlsx</option>
            #         <option value="2020年二季度.xlsx">2020年二季度.xlsx</option>
            #         <option value="2020年三季度.xlsx">2020年三季度.xlsx</option>
            #         <option value="2020年四季度.xlsx">2020年四季度.xlsx</option>
            #     </select>
            #     <input type="submit" value="确认">
            # </form>
            # <br>
            # """
        # delete_section = """
            # <!---清除特定表单-->
            # <form action="/clear" method="post">
            #     清除特定表单:
            #     <select name="table_name" id="table_name">
            #         <option value="2020年一季度.xlsx">2020年一季度.xlsx</option>
            #         <option value="2020年二季度.xlsx">2020年二季度.xlsx</option>
            #         <option value="2020年三季度.xlsx">2020年三季度.xlsx</option>
            #         <option value="2020年四季度.xlsx">2020年四季度.xlsx</option>
            #     </select>
            #     <input type="submit" value="确认">
            # </form>
            # <br>

            # <!-- 清除所有内容 -->
            # <form action="/clear_all" method="post">
            #     清除所有表单: 
            #     <input type="submit" value="清除数据库内 所有集合">
            # </form>
            # """
        login_section = f"""
            已登陆<br><br>
            名字: &nbsp <input type="text" name="operator_name" required readonly value={operator_name}> <br>
            日期: &nbsp <input type="time" name="operator_date" required readonly value={operator_date}> <br>
            时间: &nbsp <input type="time" name="operator_time" required readonly value={operator_time}> <br>
            <br>
            <form action="{url_for('initialize')}" method="post">
                <input type="submit" value="退出登录">
            </form>
            """
        

    return render_template('index.html', \
        fileUpload_section = fileUpload_section, \
        insert_section = insert_section, \
        login_section  = login_section, 
        )

# =============================================
# flask router: main menu

@app.route('/file', methods=["POST"])
def upload_file():
    save_json = False
    save_xlsx = False

    if request.method == "POST":
        # 提取文件名, 若需要使用 save（）方法保存文件 
        f = request.files.get("stuff_file")
        f_name = f.filename
        if('xlsx' not in f_name):
            # 检查文件类型是否正确
            return render_template("upload.html", message=f"上传文件失败, 错误: 文件名为{f_name} (需要为后缀是xlsx的文件)")
        else: 
            # 保存文件, 从文件读取内容, 并保存到数据库
            f.save(f'./src/temp/{f_name}') # 临时保存文件
            if(save_xlsx): f.save(f'./src/excel/{f_name}') 

            config= DB_Config(tb_name=f_name, collection_name=f_name.split('.')[0])
            # config={
            #     "tb_name" : f_name,
            #     "db_host" : 'localhost',
            #     "db_port" : 27017,
            #     "db_name" : "账户统计",
            #     "collection_name" : f_name.split('.')[0],
            # }

            # Read from Excel file 
            tb_name = config.tb_name
            excelReader = ExcelVisitor(f'./src/temp/{f_name}')
            titles      = excelReader.get_titles()
            info_table  = excelReader.get_infoTable()
            oper_table  = excelReader.get_operTable()
            os.remove(f'./src/temp/{f_name}')# 读取后删除文件
            

            # Store to custom class format 
            tableData = TableData(tb_name=tb_name, titles=titles, rows=info_table, operators=oper_table)
            tableDict = tableData.toJson()

            # Store to database
            db = MongoDatabase()
            db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
            db.insert(collection=config.collection_name, data=tableDict, _id=hash_id(config.tb_name))
            temp_mongoLoad = db.extract(collection=config.collection_name,_id=hash_id(config.tb_name))
            if(save_json): 
                JSON.save(temp_mongoLoad, JSON.PATH+f"{tb_name}.json") # 如果想暂时存储为JSON文件预览
            db.close()

            return render_template("upload.html", message=f"成功上传文件, 文件名: {f_name}")

    # 未知上传方法 (GET及其他)
    else:
            return render_template("upload.html", message=f"上传文件失败, 错误: 位置上传方法 (需要为POST)")

@app.route('/login', methods=["POST"])
def login():
    name = request.form["operator_name"]
    password = request.form["operator_pass"]
    # check_login = check_account_match(name, password) 
    check_login = ('admin' in name) and ('admin' in password)

    # 缺少检测登陆成功的机制
    if(check_login):
        session['login_state'] = True
        session['operator'] = name
        session['operator_name'] = name
        return render_template("login.html", message=f"登陆成功: 用户名为[ {name} ]")
    else: 
        return render_template("login.html", message="登陆失败: 账号或密码不匹配")

@app.route('/upload', methods=["POST"])
def upload():
    # User form upload
    form_dict = dict(request.form)

    # Extract Operator Info
    operator = {}
    operator["name"] = form_dict["operator_name"]
    operator["time"] = gen_dateTime_str()   # Use the actual upload time instead
    # operator["time"] = form_dict["operator_time"]

    return "STUFF: " + str(request_dict)


# =============================================
# flask router: table operation

# @app.route('/table_all')
def table_all():
    # Retain colleciton names from database
    db = MongoDatabase()
    db.start()
    collection_names = db.list_collections()
    db.close()
    
    # Format the colleciton names into json dict
    title = "表格名称"
    completion_title = "完成度 (%)"
    row_completed_title = "已完成行数"
    row_notComplt_title = "未完成行数"
    button_title = "操作"                # Usually empty string like ""
    button_placeholder_front = "@@@@"   # @@@@@@@@@@@@@@@@@@@@'
    button_placeholder_back  = "####"   # ####################'

    # Append to json dict
    json_collections= []
    for col_name in collection_names: 
        temp_dict = {}
        temp_dict[title] = col_name
        
        # TODO: Get completion percentages from the database 
        # (通过行的最后几行是否完成来校验行是否为完成状态)
        # completion_percent = GetCompletionPercentage(col_name = col_name)
        config=DB_Config(tb_name=f"{temp_dict[title]}.xlsx", db_host='localhost', db_port=27017, db_name="账户统计", collection_name=f"{temp_dict[title]}")
        count_row_completed   = Database_Utils.count_completedRows(config=config)
        count_row_uncompleted = Database_Utils.count_allRows(config=config) - count_row_completed
        completion_percent = Database_Utils.get_completionPercentage(config=config)

        temp_dict[row_completed_title] = str(count_row_completed)
        temp_dict[row_notComplt_title] = str(count_row_uncompleted)
        temp_dict[completion_title]    = completion_percent

        # 按钮
        button_stringBefReplacement = ""
        # Will be repalced with 更改表单 button
        button_stringBefReplacement += button_placeholder_front * 1 + f"[ {col_name}.xlsx ]" + button_placeholder_back * 1
        # Will be repalced with 删除表单 button (*3 will be repalced with option of disabled)
        if(count_row_completed == 0): button_stringBefReplacement += button_placeholder_front * 2 + f"[ {col_name}.xlsx ]" + button_placeholder_back * 2
        else: button_stringBefReplacement += button_placeholder_front * 3 + f"[ {col_name}.xlsx ]" + button_placeholder_back * 3
        temp_dict[button_title] = button_stringBefReplacement
        
        json_collections.append(temp_dict)

    if len(json_collections) == 0:
        json_collections = [{title: "数据库为空 !", row_completed_title:"", row_notComplt_title:"", completion_title:"", button_title:""}]

    # 通过完成度给表格排序
    get_percentage = lambda i:i[completion_title]
    json_collections = sorted(json_collections, key=get_percentage)

    # Using json2html to convert into table
    html_table_string = json2html.convert(json = json_collections)
    replace_dict = {
        "@@@@@@@@@@@@["   : """<form action="/table/clear" method="get"><input type="hidden" name="table_name" value='""",
        "@@@@@@@@["       : """<form action="/table/clear" method="get"><input type="hidden" name="table_name" value='""",
        "@@@@["           : """<form action='/table/show' method="get"><input type="hidden" name="table_name" value='""",
        " ]############"  : """'><input type="submit" value="删除表单(已填" disabled></form>""",
        " ]########"      : """'><input type="submit" value="删除表单(未填"></form>""",
        " ]####"          : """'><input type="submit" value="展示/更改表单"></form>""",
    }
    for replace_tuple in replace_dict.items():
        html_table_string = html_table_string.replace(replace_tuple[0], replace_tuple[1])

    # Add operator info 
    operator_infos = gen_operInfo_tup()
    operator_name  = operator_infos[0]
    operator_date  = operator_infos[1].split(' ')[0]
    operator_time  = operator_infos[1].split(' ')[1]

    # Render with tempalte
    # return html_table_string
    return render_template('table_all.html', \
        table_info = html_table_string, \
        operator_name=operator_name, \
        operator_date=operator_date, \
        operator_time=operator_time)

# @app.route('/clear', methods=["POST"])
# def DEPRECATED_clear_db_table():
    # config=DB_Config()
    # # config={
    # #     "db_host" : 'localhost',
    # #     "db_port" : 27017,
    # #     "db_name" : "账户统计",
    # # }

    # table_name = request.form['table_name']
    # table_name = table_name.replace(' ', '')
    # table_name = table_name.split('.')[0] # 去除xlsx文件后缀
    # db = MongoDatabase()
    # db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
    # db.drop(collection = table_name)
    # db.close()
    # return render_template("clear.html", message=f"操作成功: 已清除集合[ {table_name} ]")

# @app.route('/clear_all', methods=["POST"])
# def DEPRECATED_clear_database():
    # config=DB_Config()
    # # config={
    # #     "db_host" : 'localhost',
    # #     "db_port" : 27017,
    # #     "db_name" : "账户统计",
    # # }
    # db = MongoDatabase()
    # db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
    # db.close()
    # return render_template("clear.html", message=f"操作成功: 数据库中所有集合已被清除")

# @app.route('/table_clear')
def table_clear():
    config=DB_Config()
    table_name = request.args.get('table_name')
    table_name = table_name.replace(' ', '')
    table_name = table_name.split('.')[0] # 去除xlsx文件后缀
    db = MongoDatabase()
    db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
    db.drop(collection = table_name)
    db.close()
    return render_template("clear_table.html", message=f"操作成功: 已清除集合[ {table_name} ]")

# @app.route('/table', methods=["POST"])
# def DEPRECATED_table():
    # config= DB_Config()
    # # config={
    # #     "tb_name" : "",# 注意这里的文件名是带xlsx后缀的
    # #     "db_host" : 'localhost',
    # #     "db_port" : 27017,
    # #     "db_name" : "账户统计",
    # #     "collection_name" : "",# 这里则 不带xlsx后缀
    # # }
    # config.tb_name = request.form['table_name']
    # config.collection_name = (config.tb_name).split('.')[0]

    # # Read from Database
    # db = MongoDatabase()
    # db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
    # temp_mongoLoad = db.extract(collection=config.collection_name,_id=hash_id(config.tb_name))
    # db.close()

    # # Convert the result to html format for printing
    # tableData  = TableData(json=temp_mongoLoad)
    # jsonDict   = tableData.tableEdit_toJson(show_operator=True)
    # htmlString = tableData.tableEdit_toHtml(json_dict=jsonDict,show_operator=True)

    # # Add form info into string 
    # now = datetime.datetime.now()
    # day = now.date()
    # time = now.time()
    # day_str = day.__format__('%Y/%m/%d')
    # time_str = time.strftime('%H:%M:%S')
    # datetime_str = day_str+ " " + time_str
    # # print(datetime_str)
    # operator_str = session["operator_name"]

    # # Return html string rendered by template
    # return render_template('table.html', table_info=htmlString, operator_name=operator_str, operator_time=datetime_str)

# @app.route('/table_show')
def table_show(table_name,show_rows_of_keys):
    table_name = table_name.replace(" ", "")    # Remove empty spaces
    config= DB_Config()                         # 使用默认数据库设置
    config.tb_name = table_name                 # 表名字
    config.collection_name = (config.tb_name).split('.')[0]

    # Read from Database
    db = MongoDatabase()
    db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
    temp_mongoLoad = db.extract(collection=config.collection_name,_id=hash_id(config.tb_name))
    db.close()

    # Convert the result to html format for printing
    tableData  = TableData(json=temp_mongoLoad)
    htmlString = tableData.tableShow_toHtml(rows_of_keys=show_rows_of_keys, show_operator=False)

    # Add operator info 
    operator_infos = gen_operInfo_tup()
    operator_name  = operator_infos[0]
    operator_date  = operator_infos[1].split(' ')[0]
    operator_time  = operator_infos[1].split(' ')[1]

    # Return html string rendered by template
    return render_template('table.html', table_info=htmlString, operator_name=operator_name, operator_date=operator_date, operator_time=operator_time)

# @.app.route('/table_edit')
def table_edit(table_name,edit_row_key):
    table_name = table_name.replace(" ", "")    # Remove empty spaces
    config= DB_Config()                         # 使用默认数据库设置
    config.tb_name = table_name                 # 表名字
    config.collection_name = (config.tb_name).split('.')[0]

    # Read from Database
    db = MongoDatabase()
    db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
    temp_mongoLoad = db.extract(collection=config.collection_name,_id=hash_id(config.tb_name))
    db.close()

    # Convert the result to html format for printing
    tableData  = TableData(json=temp_mongoLoad)
    htmlString = tableData.tableEdit_toHtml(row_of_key=edit_row_key, show_operator=False)

    # Add operator info 
    operator_infos = gen_operInfo_tup()
    operator_name  = operator_infos[0]
    operator_date  = operator_infos[1].split(' ')[0]
    operator_time  = operator_infos[1].split(' ')[1]

    # Return html string rendered by template
    return render_template('table.html', table_info=htmlString, operator_name=operator_name, operator_date=operator_date, operator_time=operator_time)

@app.route('/table/<string:option>', methods=["GET", "POST"])
def table(option):
    # # 检测登陆状态
    # if(session['operator'] is None) and (session['operator_name'] is None):
    #     return render_template('please_login.html')

    # 如果option为all: 跳转到用户选择表格界面
    if(option=='all'):
        return table_all()

    # 如果option为clear: 清除特定表单的数据
    elif(option=='clear'):
        return table_clear()

    # 如果options为表格名: 用户选择行/预览界面
    elif(option=='show'):
        # 提取表名
        tb_name = request.args.get('table_name')

        # 提取用户允许访问的行
        op_name = session["operator_name"]
        # op_rows = GET_OPERATOR_S_ALLOWED_ROWS() #TODO:Implemnt this 
        # op_rows = None # When none it is admin by deafult 
        op_rows = [733101, 733121]

        return table_show(table_name=tb_name, show_rows_of_keys=op_rows) 

    # 如果options为表格名: 用户选择行/预览界面
    elif(option=='edit'):
        # 提取表名 / 行号
        tb_name = request.args.get('table_name')
        row_id  = request.args.get('row_id')
        return table_edit(table_name=tb_name, edit_row_key=row_id)
        # return f"Not yet implmented, reuqests: {tb_name} + {row_id}"
        

# =============================================
# main

def main():
    app.run(host='0.0.0.0', port=5000, debug=True)
    return

if __name__ == "__main__":
    main()
