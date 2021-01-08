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


# =============================================
 
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

# @app.route('/table_all')
def table_all(cur, limit, user):
    """
    展示数据库中所有存在的的列表, 
        如果是管理员, 则显示表格的完成程度(多少行,百分比)
        如果是普通用户, 则显示表格的是否完成(有权限填写的行是否全部完成)
    """
    # Retain colleciton names from database
    db = MongoDatabase()
    db.start()
    collection_names = db.list_collections()
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
        if(user == 'admin') or (user == '填报用户'):
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
            rows_complete_state = Database_Utils.check_rowCompleted(config=config, authorized_banknos=Database_Utils.get_rows(user))
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
    if(user == 'admin'):
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

    if(user == 'admin'):
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
         show_operator=True if(user=='admin') else False)

    # Add operator info 
    operator_infos = gen_operInfo_tup()
    operator_name  = operator_infos[0]
    operator_date  = operator_infos[1].split(' ')[0]
    operator_time  = operator_infos[1].split(' ')[1]

    # Return html string rendered by template
    return render_template('table_show.html', table_info=htmlString, operator_name=operator_name, operator_date=operator_date, operator_time=operator_time)

# @.app.route('/table_edit')
def table_edit_all(table_name):
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
    bank_nos = Database_Utils.get_rows(user)
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
    # bank_nos = Database_Utils.get_rows(session['operator_name'])
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
    titles      = Database_Utils.get_tableTitles(tb_name=table_name)
    table       = Database_Utils.load_table(tb_name=table_name)

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
