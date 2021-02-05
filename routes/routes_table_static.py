"""
(PARTIAL DEPRECATED)
使用layui静态数据表格的路由，包括了：
- /table/<string:option> ：         所有表格显示函数的Facade （作跳转到动态渲染的路由，不能删除）
- table_main：                      展示所有表格统计数据（主界面）
- table_show:                       编辑表格（编辑页面）
- table_edit(_all) / table_submit： 提交行更改
- table_clear                       删除表格 （不能删除）
"""


# Some built-int modules
import json
from logging import log
import logging
import os
from re import L, split
import sys
import pprint
from datetime import datetime
# import random
# from threading import ExceptHookArgs
# import time

from pymongo.message import query
# from pymongo.periodic_executor import _on_executor_deleted

from modules._Database  import MongoDatabase, DB_Config
from modules._TableData import TableData
from modules._ExcelVisitor import ExcelVisitor
from modules._JsonVisitor  import JSON
# from modules._Redis import RedisCache
from modules._Database_Utils import Database_Utils
from modules._Hash_Utils import hash_id

# from werkzeug             import utils
from app                    import app
from json2html              import json2html
from flask                  import Flask, config, render_template, flash, make_response, send_from_directory, redirect, url_for, session, request, abort
from .routes_utils           import *
from .routes_file            import *
from .debugTimer             import *
from .routes_table_dynamic   import *

def helper_getDateTime(dateTime_string):
    # 静态表格通过截止时间排序的时候需要使用的列
    try:
        date_time_obj = datetime.datetime.strptime(dateTime_string, '%Y/%m/%d %H:%M:%S')
        return date_time_obj
    except ValueError:
        try:
            date_time_obj = datetime.datetime.strptime(dateTime_string, '%Y/%m/%d %H：%M：%S')
            return date_time_obj
        except ValueError:
            return datetime.datetime.min
        
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
    upload_account_title        = "提交人"
    upload_time_title           = "提交时间"
    due_date_title              = "截止日期"

    # Append to json dict
    json_collections= []
    file_upload_html= "none"
    
    # # TODO: MAKE THIS RIGHT !!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # print('===' * 30)
    # collection_names = collection_names[sheet_indexStart:sheet_indexEnd]
    # print(sheet_indexStart)
    # print(sheet_indexEnd)
    # print(collection_names)
    # print('===' * 30)
    # # TODO: MAKE THIS RIGHT !!!!!!!!!!!!!!!!!!!!!!!!!!!!


    calculated_table_count = 1
    for col_name in collection_names: 
        calculated_table_count += 1
        # if(calculated_table_count > sheet_indexEnd):break
        # else: calculated_table_count += 1

        temp_dict = {}
        temp_dict[title] = col_name
        
        # 如果是超级用户
        # if(user == 'admin') or (user == '填报用户'):
        if(Database_Utils.user.check_admin(user)):
            # (通过行的最后几行是否完成来校验行是否为完成状态)
            config=DB_Config()
            config.tb_name = f"{temp_dict[title]}.xlsx"
            config.collection_name = f"{temp_dict[title]}"

            # 提交人/提交时间/截止日期
            tb_meta  = (Database_Utils.meta.load_tablemMeta(config.tb_name.split('.')[0]))
            if('upload_operator' in tb_meta.keys()):temp_dict[upload_account_title]=tb_meta['upload_operator']
            else:temp_dict[upload_account_title]=""
            if('upload_time' in tb_meta.keys()):temp_dict[upload_time_title]=tb_meta['upload_time']
            else:temp_dict[upload_time_title]=""
            if('due' in tb_meta.keys()):temp_dict[due_date_title]=tb_meta['due']
            else:temp_dict[due_date_title]=""

            # 统计完成度
            timer = debugTimer(f"主界面-开始统计表格: {config.tb_name}  (第{calculated_table_count-1}/{sheet_indexEnd}表格)", f"完成统计表格 (总计处理了: { tb_meta['count'] } 行 { len(tb_meta['titles']) } 列)")
            timer.start()
            completion_state      = Database_Utils.stat.completion(tb_name=config.collection_name,
                is_admin=Database_Utils.user.check_admin(session['operator_name']), 
                authorized_banknos=Database_Utils.user.get_rows(session['operator_name']))
            count_row_total       = completion_state['total']
            count_row_completed   = completion_state['completed']
            count_row_uncompleted = completion_state['uncompleted']
            completion_percent    = completion_state['percentage']
            timer.end()
            
            temp_dict[row_completed_title]  = str(count_row_completed)
            temp_dict[row_allNumRows_title] = str(count_row_total)
            temp_dict[completion_title]     = completion_percent

            # 按钮
            button_stringBefReplacement = ""
            # Will be repalced with 更改表单 button
            button_stringBefReplacement += button_placeholder_front * 1 + f"[{col_name}.xlsx ]" + button_placeholder_back * 1
            # Will be repalce with 编辑必填值 button
            button_stringBefReplacement += button_placeholder_front * 5 + f"[{col_name} ]" + button_placeholder_back * 5
            # Will be repalce with 编辑截止日期/填报说明 button
            button_stringBefReplacement += button_placeholder_front * 6 + f"[{col_name} ]" + button_placeholder_back * 6
            # Will be repalced with 删除表单 button (*3 will be repalced with option of disabled)
            if(count_row_completed == 0): button_stringBefReplacement += button_placeholder_front * 2 + f"[ {col_name}.xlsx ]" + button_placeholder_back * 2
            else: button_stringBefReplacement += button_placeholder_front * 3 + f"[{col_name}.xlsx ]" + button_placeholder_back * 3
            temp_dict[button_title] = button_stringBefReplacement

        # 如果是普通用户
        else:
            config=DB_Config()
            config.tb_name = f"{temp_dict[title]}.xlsx"
            config.collection_name = f"{temp_dict[title]}"

            # 提交人/提交时间/截止日期
            tb_meta  = (Database_Utils.meta.load_tablemMeta(config.tb_name.split('.')[0]))
            if('upload_operator' in tb_meta.keys()):temp_dict[upload_account_title]=tb_meta['upload_operator']
            else:temp_dict[upload_account_title]=""
            if('upload_time' in tb_meta.keys()):temp_dict[upload_time_title]=tb_meta['upload_time']
            else:temp_dict[upload_time_title]=""
            if('due' in tb_meta.keys()):temp_dict[due_date_title]=tb_meta['due']
            else:temp_dict[due_date_title]=""

            # 获取列表完成状态信息
            completion_state      = Database_Utils.stat.completion(tb_name=config.collection_name,
                is_admin=Database_Utils.user.check_admin(session['operator_name']), 
                authorized_banknos=Database_Utils.user.get_rows(session['operator_name']))
            count_row_total       = completion_state['total']
            count_row_completed   = completion_state['completed']
            count_row_uncompleted = completion_state['uncompleted']
            completion_percent    = completion_state['percentage']

            # temp_dict["完成状态"] = "已完成" if rows_complete_state else "未完成"
            temp_dict[row_completed_title]  = str(count_row_completed)
            temp_dict[row_allNumRows_title] = str(count_row_total)
            temp_dict[completion_title]     = str(completion_percent)

            # 按钮
            button_stringBefReplacement = ""
            # Will be repalced with 更改表单 button
            if(not count_row_uncompleted == 0):
                button_stringBefReplacement += button_placeholder_front * 1 + f"[{col_name}.xlsx ]" + button_placeholder_back * 1
                temp_dict[button_title] = button_stringBefReplacement
            else:
                button_stringBefReplacement += button_placeholder_front * 4 + f"[{col_name}.xlsx ]" + button_placeholder_back * 4
                temp_dict[button_title] = button_stringBefReplacement

        json_collections.append(temp_dict)

    if len(json_collections) == 0:
        json_collections = [{title: "数据库为空 !", row_completed_title:"", row_allNumRows_title:"", completion_title:"", button_title:""}]
    else:
        # 如果希望使用表格名称排序 (这里先使用表格名称排一遍，后续再加上其他的排序规则)
        get_key = lambda i:i[title]
        json_collections = sorted(json_collections, key=get_key, reverse=False)

        # 如果希望使用完成度排序
        # if(Database_Utils.user.check_admin(user)):
        #   get_key = lambda i:i[completion_title]
        #   json_collections = sorted(json_collections, key=get_key, reverse=False)

        # 如果希望使用截止日期排序
        get_key = lambda i : helper_getDateTime(i[due_date_title])
        json_collections = sorted(json_collections, key=get_key, reverse=False)

    # ============================

    # keep only a fraction of data
    json_collections = json_collections[sheet_indexStart: sheet_indexEnd]

    # Using json2html to convert into table
    html_table_string = json2html.convert(json = json_collections)
    html_table_string = html_table_string.replace("""<table border="1">""", """<table class="layui-table" id="table">""")

    replace_dict = {
        "@@@@@@@@@@@@@@@@@@@@@@@@[" : f"""<form style="display: inline;" action='/dueNComment/""",
        "@@@@@@@@@@@@@@@@@@@@["     : f"""<form style="display: inline;" action='/select_RequredAttribute/""",
        "@@@@@@@@@@@@@@@@["         : f"""<form style="display: inline;" action='/table/show' method="get"><input type="hidden" name="table_name"  value='""",
        "@@@@@@@@@@@@["             : f"""<form style="display: inline;" action="/table/clear" method="get"><input type="hidden" name="table_name" value='""",
        "@@@@@@@@["                 : f"""<form style="display: inline;" action="/table/clear" method="get"><input type="hidden" name="table_name" value='""",
        "@@@@["                     : f"""<form style="display: inline;" action='/table/show' method="get"><input type="hidden" name="table_name"  value='""",
        " ]########################": f"""'><input class="layui-btn layui-btn-sm "  type="submit"  value="&nbsp;&nbsp;&nbsp;&nbsp;编辑填报说明/截止日期&nbsp;&nbsp;&nbsp;&nbsp;"></form>         """,
        " ]####################"    : f"""/True'><input class="layui-btn layui-btn-sm "  type="submit"  value="&nbsp;&nbsp;&nbsp;&nbsp;编辑必填值&nbsp;&nbsp;&nbsp;&nbsp;"></form>         """,
        " ]################"        : f"""'><input class="layui-btn layui-btn-sm"  type="submit"  value="&nbsp;&nbsp;查看已完成表单&nbsp;&nbsp;"></form>         """,
        " ]############"            : f"""'><input class="layui-btn layui-btn-sm layui-btn-disabled " type="submit"  value="&nbsp;无法删除 (已填写)" ></form>       """,
        " ]########"                : f"""'><input class="layui-btn layui-btn-sm layui-btn-danger "   type="submit"  value="&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;删除表单&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"></form>                 """,
        " ]####"                    : f"""'><input class="layui-btn layui-btn-sm "  type="submit"  value="&nbsp;&nbsp;查看 / 填写表单&nbsp;&nbsp;"></form>                 """,
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
    return render_template('table_show_main.html',   \
        file_upload_section = file_upload_html,\
        table_info = html_table_string, \
        operator_name=operator_name,    \
        operator_date=operator_date,    \
        operator_time=operator_time,    \
        page_curr = page['curr'],       \
        page_limit = page['limit'],     \
        page_count = page['count'],     \
        )

@app.route('/table_clear/<string:table_name>')
def table_clear(table_name):
    """
    删除指定名称的表单
    """
    config=DB_Config()
    db = MongoDatabase()
    db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
    db.drop(collection = table_name)
    db.close()
    Database_Utils.meta.del_tablemMeta(tb_name=table_name)
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
        return redirect(url_for('show_all_tables_mainPage'))
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
        return redirect(url_for('edit_specified_table', table_name=tb_name)+'?entry=main_page')
        # op_name = session["operator_name"]                # session提取用户名
        # op_rows = Database_Utils.user.get_rows(op_name)   # 提取用户允许访问的行
        # return table_show(table_name=tb_name, show_rows_of_keys=op_rows, user=op_name) 

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
