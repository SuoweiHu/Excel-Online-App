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
from app import app

# Imported libraries
# from pymongo.periodic_executor import _on_executor_deleted
# from werkzeug   import utils
from json2html  import json2html
from flask      import Flask, config, render_template, flash, make_response, send_from_directory, redirect, url_for, session, request


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
# flask router: main page

@app.route('/', methods=["POST","GET"])
def initialize():
    session['login_state']   = False
    session['operator']      = None
    session['operator_name'] = None
    session['previous_page'] = None
    session['page']          = 0
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
    if(not session['login_state']):
        # fileUpload_section = f"<br>{'&nbsp;'*3}请登录, 以访问数据库 ... ... <br><br>"
        # insert_section     = f"<br>{'&nbsp;'*3}请登录, 以访问数据库 ... ... <br><br>"
        # delete_section = "请登录, 以访问数据库 ... ..."
        # login_section  = """
            # 登陆以获得更多权限<br><br>
            # <form action="/login" method="post">
            #     账户名:      
            #     <input type="text" name="operator_name" id=""><br>
            #     &nbsp;密码:&nbsp;&nbsp;&nbsp; 
            #     <input type="password" name="operator_pass" id=""><br>
            #     <br>
            #     <input type="submit" value="提交">
            # </form>
            # """

        return render_template('index_logged_out.html')
    elif(session['operator_name'] == "admin"):
        # fileUpload_section = """
            # <form action="/file" method="post" enctype="multipart/form-data">
            #     <input type="file" name="stuff_file"  id=""><br><br>
            #     <input type="submit" value="--- 上传 ---">
            # </form>
            # """
        # insert_section = """
            # <!---查看所有表单-->
            # <form action="/table/all" method="post">
            #     <input type="submit" value="更改/查看 已有表单">
            # </form>
            # <br>

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
        # login_section = f"""
            # 已登陆<br><br>
            # 名字: &nbsp <input type="text" name="operator_name" required readonly value={operator_name}> <br>
            # 日期: &nbsp <input type="time" name="operator_date" required readonly value={operator_date}> <br>
            # 时间: &nbsp <input type="time" name="operator_time" required readonly value={operator_time}> <br>
            # <br>
            # <form action="{url_for('initialize')}" method="post">
            #     <input type="submit" value="&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;退出登录&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;">
            # </form>
            # """
        
            # """
        return redirect('/table/all')
        return render_template('index_logged_in.html', \
            operator_name = gen_operInfo_tup()[0], \
            operator_time = gen_operInfo_tup()[1].split(' ')[1], \
            operator_date = gen_operInfo_tup()[1].split(' ')[0], \
        )
    else:
        return redirect('/table/all')

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
        f_name = f_name.replace(" ", "_")

        if('xlsx' not in f_name):
            # 检查文件类型是否正确
            return render_template("redirect_fileUploaded.html", message=f"上传文件失败, 错误: 文件名为{f_name} (需要为后缀是xlsx的文件)")
        elif(f_name.split('.')[0] in Database_Utils.list_collections()):
            # 检查文件是否已经存在
            return render_template("redirect_fileUploaded.html", message=f"上传文件失败, 错误: 文件/集合已经存在", table_name = f_name)
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

            return render_template("redirect_fileUploaded.html", message=f"成功上传文件, 文件名: {f_name}", table_name = f_name)

    # 未知上传方法 (GET及其他)
    else:
            return render_template("redirect_fileUploaded.html", message=f"上传文件失败, 错误: 位置上传方法 (需要为POST)")

@app.route('/login', methods=["POST"])
def login():
    name    = request.form["operator_name"]
    password = request.form["operator_pass"]
    # check_login = check_account_match(name, password) 
    # check_login = ('admin' in name) and ('admin' in password)
    db_password = Database_Utils.get_password(name)
    check_login = (db_password is not None) and (password == db_password)

    # 缺少检测登陆成功的机制
    if(check_login):
        session['login_state'] = True
        session['operator'] = name
        session['operator_name'] = name
        return render_template("redirect_login.html", message=f"登陆成功: 用户名为[ {name} ]")
    else: 
        return render_template("redirect_login.html", message="登陆失败: 账号或密码不匹配")

# @app.route('/upload', methods=["POST"])
# def DEPERCATED_upload():
    # # User form upload
    # form_dict = dict(request.form)

    # # Extract Operator Info
    # operator = {}
    # operator["name"] = form_dict["operator_name"]
    # operator["time"] = gen_dateTime_str()   # Use the actual upload time instead
    # # operator["time"] = form_dict["operator_time"]

    # return "STUFF: " + str(request_dict)


# =============================================
# flask router: table operation
# @app.route('/table_all')
def table_all():
    # Retain colleciton names from database
    db = MongoDatabase()
    db.start()
    collection_names = db.list_collections()
    db.close()

    # Take a fraction of the data and display them
    page = {}
    if(request.args.get('curr') is None) or (request.args.get('limit') is None):
        page['curr']  = 1
        page['limit'] = 10
        page['count'] = len(collection_names)
    else:
        page['curr']  = int(request.args.get('curr'))
        page['limit'] = int(request.args.get('limit'))
        page['count'] = len(collection_names)

    # Take only the fraction of sheets to display
    sheet_indexStart = (page['curr'] - 1) * page['limit']
    sheet_indexEnd   = sheet_indexStart   + page['limit'] # exclusive of the index
    if(sheet_indexEnd > len(collection_names)): sheet_indexEnd = len(collection_names)
    
    # Format the colleciton names into json dict
    title = "表格名称"
    completion_title = "完成度 (%)"
    row_completed_title = "完成-行数"
    row_allNumRows_title = "全部-行数"
    button_title = "操作"                # Usually empty string like ""
    button_placeholder_front = "@@@@"   # @@@@@@@@@@@@@@@@@@@@'
    button_placeholder_back  = "####"   # ####################'

    # Append to json dict
    json_collections= []
    file_upload_html= "none"
    for col_name in collection_names: 
        temp_dict = {}
        temp_dict[title] = col_name
        
        # 如果是超级用户
        if(session["operator_name"] == 'admin'):
            # (通过行的最后几行是否完成来校验行是否为完成状态)
            config=DB_Config(tb_name=f"{temp_dict[title]}.xlsx", db_host='localhost', db_port=27017, db_name="账户统计", collection_name=f"{temp_dict[title]}")
            count_row_completed   = Database_Utils.count_completedRows(config=config)
            count_row_uncompleted = Database_Utils.count_allRows(config=config) - count_row_completed
            completion_percent = Database_Utils.get_completionPercentage(config=config)

            temp_dict[row_completed_title] = str(count_row_completed)
            temp_dict[row_allNumRows_title] = str(count_row_uncompleted+count_row_completed)
            # temp_dict["完成/全部行数"] = str(count_row_completed) + " / " + str(count_row_uncompleted+count_row_completed)
            temp_dict[completion_title]    = completion_percent

            # 按钮
            button_stringBefReplacement = ""
            # Will be repalced with 更改表单 button
            button_stringBefReplacement += button_placeholder_front * 1 + f"[{col_name}.xlsx ]" + button_placeholder_back * 1
            # Will be repalced with 删除表单 button (*3 will be repalced with option of disabled)
            if(count_row_completed == 0): button_stringBefReplacement += button_placeholder_front * 2 + f"[ {col_name}.xlsx ]" + button_placeholder_back * 2
            else: button_stringBefReplacement += button_placeholder_front * 3 + f"[{col_name}.xlsx ]" + button_placeholder_back * 3
            temp_dict[button_title] = button_stringBefReplacement

        # 如果是普通用户
        else:
            config=DB_Config(tb_name=f"{temp_dict[title]}.xlsx", db_host='localhost', db_port=27017, db_name="账户统计", collection_name=f"{temp_dict[title]}")
            rows_complete_state = Database_Utils.check_rowCompleted(config=config, row_ids=Database_Utils.get_authorizedRows(session['operator_name']))
            temp_dict["完成状态"] = "已完成" if rows_complete_state else "未完成"
            # 按钮
            button_stringBefReplacement = ""
            # Will be repalced with 更改表单 button
            if(not rows_complete_state):
                button_stringBefReplacement += button_placeholder_front * 1 + f"[{col_name}.xlsx ]" + button_placeholder_back * 1
                temp_dict[button_title] = button_stringBefReplacement
            else:
                button_stringBefReplacement += button_placeholder_front * 4 + f"[{col_name}.xlsx ]" + button_placeholder_back * 4
                temp_dict[button_title] = button_stringBefReplacement

        json_collections.append(temp_dict)

    if len(json_collections) == 0:
        json_collections = [{title: "数据库为空 !", row_completed_title:"", row_allNumRows_title:"", completion_title:"", button_title:""}]

    get_title = lambda i:i[title]
    json_collections = sorted(json_collections, key=get_title)
    if(session["operator_name"] == 'admin'):
        # 通过完成度给表格排序
        get_percentage = lambda i:i[completion_title]
        json_collections = sorted(json_collections, key=get_percentage)

    # keep only a fraction of data
    json_collections = json_collections[sheet_indexStart: sheet_indexEnd]

    # Using json2html to convert into table
    html_table_string = json2html.convert(json = json_collections)
    html_table_string = html_table_string.replace("""<table border="1">""", """<table class="layui-table">""")

    replace_dict = {
        "@@@@@@@@@@@@@@@@["     : """<form style="display: inline;" action='/table/show' method="get"><input type="hidden" name="table_name"  value='""",
        "@@@@@@@@@@@@["         : """<form style="display: inline;" action="/table/clear" method="get"><input type="hidden" name="table_name" value='""",
        "@@@@@@@@["             : """<form style="display: inline;" action="/table/clear" method="get"><input type="hidden" name="table_name" value='""",
        "@@@@["                 : """<form style="display: inline;" action='/table/show' method="get"><input type="hidden" name="table_name"  value='""",
        " ]################"    : """'><input class="layui-btn layui-btn-sm"  type="submit"  value="&nbsp;&nbsp;查看已完成表单&nbsp;&nbsp;"></form>         """,
        " ]############"        : """'><input class="layui-btn layui-btn-sm layui-btn-disabled " type="submit"  value="&nbsp;删除表单 (已填写)" disabled></form>       """,
        " ]########"            : """'><input class="layui-btn layui-btn-sm layui-btn-danger "   type="submit"  value="&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;删除表单&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"></form>                 """,
        " ]####"                : """'><input class="layui-btn layui-btn-sm layui-btn-primary "  type="submit"  value="&nbsp;&nbsp;查看 / 填写表单&nbsp;&nbsp;"></form>                 """,
    }
    for replace_tuple in replace_dict.items():
        html_table_string = html_table_string.replace(replace_tuple[0], replace_tuple[1])

    # Add operator info 
    operator_infos = gen_operInfo_tup()
    operator_name  = operator_infos[0]
    operator_date  = operator_infos[1].split(' ')[0]
    operator_time  = operator_infos[1].split(' ')[1]

    if(session['operator_name'] == 'admin'):
            # 开启文件上传功能
            file_upload_html = """inline"""

    # Render with tempalte
    # return html_table_string
    return render_template('table_all.html',   \
        file_upload_section = file_upload_html,\
        table_info = html_table_string, \
        operator_name=operator_name,    \
        operator_date=operator_date,    \
        operator_time=operator_time,    \
        page_curr = page['curr'],       \
        page_limit = page['limit'],     \
        page_count = page['count'],     \
        )

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
    # return render_template("redirect_clearAllTable.html", message=f"操作成功: 已清除集合[ {table_name} ]")

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
    # return render_template("redirect_clearAllTable.html", message=f"操作成功: 数据库中所有集合已被清除")

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
    return render_template("redirect_tableCleaned.html", message=f"操作成功: 已清除集合[ {table_name} ]")

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
    # return render_template('table_show.html', table_info=htmlString, operator_name=operator_str, operator_time=datetime_str)

# @app.route('/table_show')
def table_show(table_name,show_rows_of_keys):
    # table_name = table_name.replace(" ", "")  # Remove empty spaces
    config= DB_Config()                         # 使用默认数据库设置
    config.tb_name = table_name                 # 表名字
    config.collection_name = (config.tb_name).split('.')[0]

    # print(f"|{table_name}|")
    # print(f"|{table_name}|")

    # Read from Database
    db = MongoDatabase()
    db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
    temp_mongoLoad = db.extract(collection=config.collection_name,_id=hash_id(config.tb_name))
    db.close()

    # Convert the result to html format for printing
    tableData  = TableData(json=temp_mongoLoad)
    htmlString = tableData.tableShow_toHtml(rows_of_keys=show_rows_of_keys,\
         show_operator=True if(session['operator_name']=='admin') else False)

    # Add operator info 
    operator_infos = gen_operInfo_tup()
    operator_name  = operator_infos[0]
    operator_date  = operator_infos[1].split(' ')[0]
    operator_time  = operator_infos[1].split(' ')[1]

    # Return html string rendered by template
    return render_template('table_show.html', table_info=htmlString, operator_name=operator_name, operator_date=operator_date, operator_time=operator_time)

# @.app.route('/table_edit')
def table_edit(table_name,edit_row_key):
    # table_name = table_name.replace(" ", "")    # Remove empty spaces
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
    return render_template('table_show.html', table_info=htmlString, operator_name=operator_name, operator_date=operator_date, operator_time=operator_time)

# @app.route('/table_submit')
def table_submit(table_name,row_id):
    # Upload the updated data to mongodb database
    titles      = Database_Utils.get_tableTitles(tb_name=table_name)
    origin_dict = Database_Utils.load_table(tb_name=table_name)
    for title in titles:
        if(request.form.get(title) is not None):
            origin_dict['data'][row_id][title] = request.form.get(title)
    origin_dict['data'][row_id]['操作员']   = session['operator_name']
    origin_dict['data'][row_id]['操作时间'] = gen_dateTime_str()

    # pprint.pprint(origin_dict['data'][row_id], indent=4)
    Database_Utils.save_table(tb_name=table_name, data=origin_dict)

    return render_template('redirect_tableSubmitted.html', table_name=table_name)

@app.route('/table/<string:option>', methods=["GET", "POST"])
def table(option):
    # 检测登陆状态
    if(session['operator'] is None) and (session['operator_name'] is None):
        return render_template('redirect_prompt.html')

    # 如果option为all: 跳转到用户选择表格界面
    if(option=='all'):
        return table_all()

    # 如果option为clear: 清除特定表单的数据
    elif(option=='clear'):
        return table_clear()

    # 如果options为show: 用户选择(多)行/预览界面
    elif(option=='show'):
        # 提取表名
        tb_name = request.args.get('table_name')

        # 提取用户允许访问的行
        op_name = session["operator_name"]
        op_rows = Database_Utils.get_authorizedRows(user_name=op_name)
        print(tb_name)
        return table_show(table_name=tb_name, show_rows_of_keys=op_rows) 

    # 如果options为表格名: 用户编辑行界面
    elif(option=='edit'):
        # 提取表名 / 行号
        tb_name = request.args.get('table_name')
        row_id  = request.args.get('row_id')
        return table_edit(table_name=tb_name, edit_row_key=row_id)
    
    # 如果option为submit: 提交数据然后返回show界面 (POST)
    elif(option=='submit'):
        table_name  = request.form.get('table_name')
        row_id      = request.form.get('row_id')
        return table_submit(table_name=table_name, row_id=row_id)
