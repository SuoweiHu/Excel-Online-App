# Some built-int modules
import json
from logging import log
import logging
import os
import sys
import pprint
import datetime
import random

from modules._Database  import MongoDatabase, DB_Config
from modules._TableData import TableData
from modules._ExcelVisitor import ExcelVisitor
from modules._JsonVisitor  import JSON
# from modules._Redis import RedisCache
from modules._Database_Utils import Database_Utils
from modules._Hash_Utils import hash_id

# from pymongo.periodic_executor import _on_executor_deleted
# from werkzeug   import utils
from app import app
from json2html  import json2html
from flask      import Flask, config, render_template, flash, make_response, send_from_directory, redirect, url_for, session, request

from routes_utils import *
# from routes_table import *
from routes_file  import *
# from routes_login import *



# =============================================
# 手动渲染表格

# @app.route('/table_main')
def table_main(cur, limit, user):
    """
    展示数据库中所有存在的的列表, 
        如果是管理员, 则显示表格的完成程度(多少行,百分比)
        如果是普通用户, 则显示表格的是否完成(有权限填写的行是否全部完成)
    """
    # Retain colleciton names from database
    db = MongoDatabase()
    db.start()
    collection_names = db.list_tableData_collectionNames()
    db.close()

    # Take a fraction of the data and display them
    page = {}
    if(cur is None) or (limit is None):
        page['curr']  = 1
        page['limit'] = 10
        page['count'] = len(collection_names)
    else:
        page['curr']  = int(cur)
        page['limit'] = int(limit)
        page['count'] = len(collection_names)

    # Take only the fraction of sheets to display
    sheet_indexStart = (page['curr'] - 1) * page['limit']
    sheet_indexEnd   = sheet_indexStart   + page['limit'] # exclusive of the index
    if(sheet_indexEnd > len(collection_names)): sheet_indexEnd = len(collection_names)
    
    # Format the colleciton names into json dict
    title                       = "表格名称"
    completion_title            = "完成度 (%)"
    row_completed_title         = "完成-行数"
    row_allNumRows_title        = "全部-行数"
    button_title                = "操作"                 # Usually empty string like ""
    button_placeholder_front    = "@@@@"                # @@@@@@@@@@@@@@@@@@@@'
    button_placeholder_back     = "####"                # ####################'

    # Append to json dict
    json_collections= []
    file_upload_html= "none"
    for col_name in collection_names: 
        temp_dict = {}
        temp_dict[title] = col_name
        
        # 如果是超级用户
        # if(user == 'admin') or (user == '填报用户'):
        if(Database_Utils.user.check_admin(user)):
            # (通过行的最后几行是否完成来校验行是否为完成状态)
            config=DB_Config()
            config.tb_name = f"{temp_dict[title]}.xlsx"
            config.collection_name = f"{temp_dict[title]}"

            count_row_completed   = Database_Utils.stat.count_completedRows(config=config)
            count_row_uncompleted = Database_Utils.stat.count_allRows(config=config) - count_row_completed
            completion_percent    = Database_Utils.stat.get_completionPercentage(config=config)

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
            config=DB_Config()
            config.tb_name = f"{temp_dict[title]}.xlsx"
            config.collection_name = f"{temp_dict[title]}"

            # 获取列表完成状态信息
            rows_uncompleted, rows_complted, rows_all_, completion_percentage_, rows_complete_state = \
                Database_Utils.stat.get_completionState(config=config, authorized_banknos=Database_Utils.user.get_rows(user))

            # temp_dict["完成状态"] = "已完成" if rows_complete_state else "未完成"
            temp_dict[row_completed_title]  = str(rows_complted)
            temp_dict[row_allNumRows_title] = str(rows_all_)
            temp_dict[completion_title]     = str(completion_percentage_)

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

    # if(user == 'admin'):
    if(Database_Utils.user.check_admin(user)):
        # 通过完成度给表格排序
        get_percentage = lambda i:i[completion_title]
        json_collections = sorted(json_collections, key=get_percentage)

    # keep only a fraction of data
    json_collections = json_collections[sheet_indexStart: sheet_indexEnd]

    # Using json2html to convert into table
    html_table_string = json2html.convert(json = json_collections)
    html_table_string = html_table_string.replace("""<table border="1">""", """<table class="layui-table" id="table">""")

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

    # if(user == 'admin'):
    if(Database_Utils.user.check_admin(user)):
            # 开启文件上传功能
            file_upload_html = """inline"""

    # Render with tempalte
    # return html_table_string
    return render_template('table_main.html',   \
        file_upload_section = file_upload_html,\
        table_info = html_table_string, \
        operator_name=operator_name,    \
        operator_date=operator_date,    \
        operator_time=operator_time,    \
        page_curr = page['curr'],       \
        page_limit = page['limit'],     \
        page_count = page['count'],     \
        )

# @app.route('/table_clear')
def table_clear(table_name):
    """
    删除指定名称的表单
    """
    config=DB_Config()
    db = MongoDatabase()
    db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
    db.drop(collection = table_name)
    db.close()
    return render_template("redirect_tableCleaned.html", message=f"操作成功: 已清除集合[ {table_name} ]")

# @app.route('/table_show')
def table_show(table_name,show_rows_of_keys, user):
    """
    展示指定名字的表单(根据用户权限展示有限的行)
    """
    config= DB_Config()                         # 使用默认数据库设置
    config.tb_name = table_name                 # 表名字
    config.collection_name = (config.tb_name).split('.')[0]

    table_name = config.collection_name
    db = MongoDatabase()
    db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
    temp_mongoLoad = db.get_documents(collection=table_name)
    db.close()

    # Convert the result to html format for printing
    tableData  = TableData(json=temp_mongoLoad,tb_name=table_name)
    htmlString = tableData.tableShow_toHtml(rows_of_keys=show_rows_of_keys,\
        #  show_operator=True if(user == 'admin') else False)
         show_operator=True if(Database_Utils.user.check_admin(user)) else False)

    # Add operator info 
    operator_infos = gen_operInfo_tup()
    operator_name  = operator_infos[0]
    operator_date  = operator_infos[1].split(' ')[0]
    operator_time  = operator_infos[1].split(' ')[1]

    # Return html string rendered by template
    return render_template('table_show.html', table_info=htmlString, operator_name=operator_name, operator_date=operator_date, operator_time=operator_time)

# @.app.route('/table_edit')
def table_edit_all(table_name, user):
    """
    修改指定表格的指定行(先检查现用户是否有权限更改要求的行)
    """
    config= DB_Config()                         # 使用默认数据库设置
    config.tb_name = table_name                 # 表名字
    config.collection_name = (config.tb_name).split('.')[0]

    # Read from Database
    table_name = config.collection_name
    db = MongoDatabase()
    db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
    temp_mongoLoad = db.get_documents(collection=table_name)
    db.close()

    # Convert the result to html format for printing
    tableData  = TableData(json=temp_mongoLoad, tb_name=table_name)
    bank_nos = Database_Utils.user.get_rows(user)
    row_ids  = tableData.get_row_id(bank_nos=bank_nos)

    # htmlString = tableData.tableEdit_toHtml(row_of_key=edit_row_key, show_operator=False)
    htmlString = tableData.tableEdit_toHtml_s(row_of_keys=row_ids, show_operator=False)

    # Add operator info 
    operator_infos = gen_operInfo_tup()
    operator_name  = operator_infos[0]
    operator_date  = operator_infos[1].split(' ')[0]
    operator_time  = operator_infos[1].split(' ')[1]

    # Return html string rendered by template
    return render_template('table_show.html',\
        table_info=htmlString,\
        operator_name=operator_name,\
        operator_date=operator_date,\
        operator_time=operator_time)

# @.app.route('/table_edit')
def table_edit(table_name,edit_row_key):
    """
    修改指定表格的指定行(先检查现用户是否有权限更改要求的行)
    """
    config= DB_Config()                         # 使用默认数据库设置
    config.tb_name = table_name                 # 表名字
    config.collection_name = (config.tb_name).split('.')[0]

    # Read from Database
    table_name = config.collection_name
    db = MongoDatabase()
    db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
    temp_mongoLoad = db.get_documents(collection=table_name)
    db.close()

    # Convert the result to html format for printing
    tableData  = TableData(json=temp_mongoLoad, tb_name=table_name)
    # bank_nos = Database_Utils.user.get_rows(session['operator_name'])
    # row_ids  = tableData.get_row_id(bank_nos=bank_nos)

    htmlString = tableData.tableEdit_toHtml(row_of_key=edit_row_key, show_operator=False)
    # htmlString = tableData.tableEdit_toHtml_s(row_of_keys=row_ids, show_operator=False)

    # Add operator info 
    operator_infos = gen_operInfo_tup()
    operator_name  = operator_infos[0]
    operator_date  = operator_infos[1].split(' ')[0]
    operator_time  = operator_infos[1].split(' ')[1]

    # Return html string rendered by template
    return render_template('table_show.html',\
        table_info=htmlString,\
        operator_name=operator_name,\
        operator_date=operator_date,\
        operator_time=operator_time)

# @app.route('/table_submit')
def table_submit(table_name,row_id, user):
    """
    上传用户对于特定表格特定行的修改, 并附上操作时间和用户名信息
    """
    # Upload the updated data to mongodb database
    titles      = Database_Utils.table.get_tableTitles(tb_name=table_name)
    table       = Database_Utils.table.load_table(tb_name=table_name)

    row_index  = table.ids.index(row_id)
    # print(table.rows[table.ids.index(row_id)])

    for title in titles:
        if(request.form.get(title) is not None) and (len(request.form.get(title).replace(' ', '')) != 0):
            # print(request.form.get(title),"YAY")
            item_index = table.titles.index(title)
            table.rows[row_index][item_index] = request.form.get(title)
    table.operators[row_index][0] = user
    table.operators[row_index][1] = gen_dateTime_str()

    table_clear(table_name=table_name)
    # print(table.rows[table.ids.index(row_id)])
    Database_Utils.save_table(tb_name=table_name, data=table.toJson())

    return render_template('redirect_tableSubmitted.html', table_name=table_name)

@app.route('/table/<string:option>', methods=["GET", "POST"])
def table(option):
    """
    根据不同的option跳转到不同的 上传/填表/展示页面
    """
    # 检测登陆状态, 如果为登陆则返回登陆界面
    if(session['operator'] is None) and (session['operator_name'] is None):
        return render_template('redirect_prompt.html')

    # 如果option为all: 跳转到用户选择表格界面
    if(option=='all'):
        cur=request.args.get('curr')                # 提取现在的页数
        limit=request.args.get('limit')             # 提取最大显示行数
        user=session["operator_name"]               # 提取表格名称
        return table_main(cur, limit, user)

    # 如果option为clear: 清除特定表单的数据
    elif(option=='clear'):
        table_name = request.args.get('table_name') # 提取表格名称
        table_name = table_name.replace(' ', '')    # 去除入参中的空格 (因为是替换字符做的form, 可能会有这类问题)
        table_name = table_name.split('.')[0]       # 去除xlsx文件后缀
        return table_clear(table_name=table_name)

    # 如果options为show: 用户选择(多)行/预览界面
    elif(option=='show'):
        tb_name = request.args.get('table_name')    # 提取表名
        tb_name = tb_name.split('.')[0]
        return redirect(f'/edit/{tb_name}')
        op_name = session["operator_name"]          # session提取用户名
        op_rows = Database_Utils.user.get_rows(op_name)  # 提取用户允许访问的行
        return table_show(table_name=tb_name, show_rows_of_keys=op_rows, user=op_name) 

    # 如果options为表格名: 用户编辑行界面
    elif(option=='edit'):
        tb_name = request.args.get('table_name')    # 提取表名
        row_id  = request.args.get('row_id')        # 提取行uuid (注意: 这里的row_id不是行号 !!!)
        return table_edit(table_name=tb_name, edit_row_key=row_id)
        # 不通过入参提取表明, 直接显示用户有权限访问的所有表单
    
    # 如果option为submit: 提交数据然后返回show界面 (POST)
    elif(option=='submit'):
        table_name  = request.form.get('table_name')# 提取表名
        row_id      = request.form.get('row_id')    # 提取行uuid (注意: 这里的row_id不是行号 !!!)
        return table_submit(table_name=table_name, row_id=row_id, user=session["operator_name"])

    # 如果option为show_edit: 展示使用layui框架渲染出来的表格, 且可以通过submit event listener使用javascript为数据进行提交
    elif(option=='show_edit'): 
        return

    else:
        app.logging.warn("WARNING, User attempts to access URL with an invalid table option .")
        abort(404)

# =============================================
# 自动渲染表格

@app.route('/file', methods=["POST"])
def upload_file():
    """
    上传文件, 跳转到中介页面显示 “上传成功/失败”, 然后进入该表格的展示页面/ 回到主界面
    """

    if request.method == "POST":
        f = request.files.get("stuff_file")         # 提取文件
        f_name = f.filename                         # 提取文件名, 若在后面需要使用 save() 方法保存文件 
        f_name = f_name.replace(" ", "_")           # 去除空格字符 (因为后面对于空格的识别会出现问题)
        return route_upload_file(f=f, f_name=f_name)

    else:                                                    
        return render_template("redirect_fileUploaded.html",\
            message=f"上传文件失败, 错误: 位置上传方法 (需要为POST)")

@app.route('/data/<string:table_name>')
def export_table_data(table_name): 
    """
    数据接口
    """
    show_operator        = True   # 是否展示操作员信息
    authorization_inedx  = 0      # 用于确认用户权限的列的序号 (这里 0 指的是 ‘行号’ 在标题的第一个位置)
    # authorized_rows      = [733101,733121,733131,733141,733151,733165,733177,733189,733201,733213,733225]
    authorized_rows      = Database_Utils.user.get_rows(session['operator_name'])
    authorized_rows      = [str(i) for i in authorized_rows]
    

    # ========================================
    # Layui数据接口 默认返回属性
    code  = 0  # 0 means success
    msg   = ""
    count = 1000
    data = []

    # 从数据库读取对应表格
    table_data = Database_Utils.table.load_table(table_name)
    for i in range(len(table_data.rows)):
        if(table_data.rows[i][authorization_inedx] in authorized_rows) or (Database_Utils.user.check_admin(session['operator_name'])):
            temp = {}

            # UUID
            _id  = table_data.ids[i]
            temp['_id'] = _id

            # 数据
            _row = table_data.rows[i]
            for j in range(len(table_data.titles)):
                    _cell  =_row[j]
                    _title =  table_data.titles[j]
                    temp[_title] = _cell

            # 操作员
            if(show_operator):
                for j in range(len(table_data.operator_titles)):
                    op_title =  table_data.operator_titles[j]
                    op_data  =  table_data.operators[i][j]
                    temp[op_title] = op_data

            # 添加当前行
            data.append(temp)
    
    return {"code":code, "msg":msg, "count":count, "data":data}

@app.route('/edit/<string:table_name>')
def edit_specified_table(table_name):

    show_operator        = True   # 是否展示操作员信息
    authorization_inedx  = 0      # 用于确认用户权限的列的序号 (这里 0 指的是 ‘行号’ 在标题的第一个位置)

    # ========================================
    # 设置行属性 
    column_titles = Database_Utils.table.get_tableTitles(table_name) 
    if(show_operator): column_titles += TableData.operator_titles
    # (这里的id:title映射将被Jinja2赋值到 layui数据表单中的 每行的field上)
    column_ids    = [i for i in column_titles]
    column_dict   = {column_ids[i]:column_titles[i] for i in range(len(column_titles))}

    # 使用模版渲染表格
    return render_template(
        'table_show_edit.html',\
        column_dict         = column_dict,\
        table_name          = table_name, \
        authorization_title = column_titles[authorization_inedx], \
        operator_title      = TableData.operator_titles,\
        table_meta          = Database_Utils.meta.load_tablemMeta(tb_name=table_name)
        )

@app.route('/submit',methods=["POST"])
def submit_specified_table():
    """
    接受Ajax POST上传请求的路由, 更新数据库中特定集合(对应表格)的特定文件(对应行)
    """

    _id        = request.form.get('_id')
    table_name = request.form.get('table_name')
    req_data   = dict(request.form)
    op_name = session['operator_name']
    op_time = gen_dateTime_str()

    # DEBUG LOGGGING 
    debug_string = f""" 
    Saving changes for
      table  = {table_name}
      row_id = {_id}
      data   = {req_data}

    Action performed by
      user = {op_name}
      time = {op_time}
    """
    app.logger.debug(debug_string)

    # print("\n"*2)
    # print(_id)
    # print(table_name)
    # print(req_data)
    # print(op_name)
    # print(op_time)
    # print("\n"*2)

    origi_document = Database_Utils.row.get_table_row(table_name=table_name, row_id=_id)
    modif_document = origi_document.copy()
    for title,cell_data in origi_document['data'].items():
        modif_data = req_data[title] 
        if isinstance(modif_data, list): modif_data = modif_data[0]
        modif_document['data'][title] = modif_data
    modif_document['user']['name'] = op_name
    modif_document['user']['time'] = op_time
    Database_Utils.row.set_table_row(table_name=table_name, row_id=_id, data=modif_document)
    origi_document = Database_Utils.row.get_table_row(table_name=table_name, row_id=_id)

    return "Success !"


