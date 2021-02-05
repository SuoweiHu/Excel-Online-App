"""
使用layui动态数据表格的路由，包括了：
- /api/dataEdit :                   编辑页面的数据接口
- /api/dataMain/<string:option>：   主界面的数据接口
- /api/submit_row :                 提交行的提交接口
- /multiChoice/<string:tb_name>/<string:title>/<string:_id> 当点击预设单元格的显示函数
- /submit_multiChoice               提交预设单元格
- /api/toggle_archive：             切换表格归档状态
- /api/delete_table：               删除表格的请求路由
- /main                             模版页面渲染 - 主界面
- /edit/<string:table_name>         模版页面渲染  - 编辑界面
"""

# Some built-int modules
# import json
from logging import log
# import logging
# import os
# from re import L, search, split
# import sys
# import pprint
# from datetime import datetime
# from typing import Optional
# import random
# from threading import ExceptHookArgs
# import time

from pymongo.message import query
# from pymongo.periodic_executor import _on_executor_deleted

from modules._Database  import MongoDatabase, DB_Config
from modules._TableData import TableData
# from modules._ExcelVisitor import ExcelVisitor
# from modules._JsonVisitor  import JSON
# from modules._Redis import RedisCache
from modules._Database_Utils import Database_Utils
from modules._Hash_Utils import hash_id

# from werkzeug             import utils
# from json2html              import json2html
from app                    import app
from flask                  import Flask, config, render_template, flash, make_response, send_from_directory, redirect, url_for, session, request
from routes_utils           import *
from routes_file            import *
from debugTimer             import *
from routes_table_static    import *

# DEPRECATED
# @app.route('/data_all/<string:table_name>')
# def export_table_data_all(table_name):
    # """
    # 自动渲染表格 - 数据接口
    # """
    # show_operator        = True   # 是否展示操作员信息
    # # authorization_inedx  = 0    # 用于确认用户权限的列的序号 (这里 0 指的是 ‘行号’ 在标题的第一个位置)
    # # authorized_rows      = [733101,733121,733131,733141,733151,733165,733177,733189,733201,733213,733225]
    # authorized_rows      = Database_Utils.user.get_rows(session['operator_name'])
    # authorized_rows      = [str(i) for i in authorized_rows]

    # # ========================================
    # # Layui数据接口 默认返回属性
    # code  = 0  # 0 means success
    # msg   = ""
    # count = 0
    # data = []

    # sort = (None,None)
    # if('field' in dict(request.args).keys()):
    #     key   =  request.args.get('field')
    #     if(key == "操作员"):    key = 'user.name'
    #     elif(key == "时间"):    key = 'user.time' 
    #     else:                  key = 'data.' + key
    #     order = (-1) if(request.args.get('order') == 'desc') else (1)
    #     sort  = (key, order)
    # else:
    #     sort = (None, None) 

    # app.logger.debug(f"\t\t重新获得信息")
    # app.logger.debug(f"\t\t排序信息:{sort}")

    # # 从数据库读取对应表格
    # role  = ("管理员") if Database_Utils.user.check_admin(session['operator_name']) else ("普通用户")
    # timer = debugTimer(f"开始获取表格 (用户:{session['operator_name']}, 权限: {role})", "获取表格完毕")
    # timer.start()
    # # 生成查询问句
    # if(Database_Utils.user.check_admin(session['operator_name'])):row_query = {}
    # else:row_query = {'data.行号': {'$in': authorized_rows}}
    # # 尝试获取数据（如果不存在数据则会抛出RuntimeError错误）
    # try: 
    #     table_data = Database_Utils.table.load_table(tb_name=table_name, search_query=row_query, sort=sort)
    #     print(table_data.toJson)
    # except RuntimeError as e: 
    #     app.logger.debug(f"\t\t{e}")
    #     emptyTable_json = dict({})
    #     table_data = TableData(json=emptyTable_json, tb_name=table_show)
    # timer.end()

    # # 处理获得的文档成为可被Juinja2渲染的格式
    # for i in range(len(table_data.rows)):
    #     # if(table_data.rows[i][authorization_inedx] in authorized_rows) or (Database_Utils.user.check_admin(session['operator_name'])):
    #     temp = {}
    #     # UUID
    #     _id  = table_data.ids[i]
    #     temp['_id'] = _id
    #     # 数据
    #     _row = table_data.rows[i]
    #     for j in range(len(table_data.titles)):
    #             _cell  =_row[j]
    #             _title =  table_data.titles[j]
    #             temp[_title] = _cell
    #     # 操作员
    #     if(show_operator):
    #         for j in range(len(table_data.operator_titles)):
    #             op_title =  table_data.operator_titles[j]
    #             op_data  =  table_data.operators[i][j]
    #             temp[op_title] = op_data
    #     # 添加当前行
    #     data.append(temp)

    # count = len(data)
    # return {"code":code, "msg":msg, "count":count, "data":data}

# 编辑页面 - 数据接口
@app.route('/api/dataEdit')
def apiData_dataEdit(): 
    """
    获取”编辑页面“的表格的数据接口
    """

    # 获取 表格信息
    table_name = request.args['tb_name']
    app.logger.info('正在访问编辑界面数据接口, 表格名:'+table_name)

    # 获取 操作员信息
    show_operator           = True   # 是否展示操作员信息
    # authorization_inedx   = 0    # 用于确认用户权限的列的序号 (这里 0 指的是 ‘行号’ 在标题的第一个位置)
    # authorized_rows       = [733101,733121,733131,733141,733151,733165,733177,733189,733201,733213,733225]
    authorized_rows         = Database_Utils.user.get_rows(session['operator_name'])
    authorized_rows         = [str(i) for i in authorized_rows]

    # 获取 分页请求
    page  = int(request.args['page'])
    limit = int(request.args['limit'])
    start = (page - 1) * limit
    end   = start + limit

    # ========================================
    # 返回 获取到的数据

    # Layui数据接口 默认返回属性
    code  = 0  # 0 means success 
    msg   = ""
    count = 0
    data = []

    # 使用其中一列进行排序
    sort = (None,None)
    if('field' in dict(request.args).keys()):
        key   =  request.args.get('field')
        if(key == "操作员"):    key = 'user.name'
        elif(key == "时间"):    key = 'user.time' 
        else:                  key = 'data.' + key
        order = (-1) if(request.args.get('order') == 'desc') else (1)
        sort  = (key, order)
        app.logger.debug(f"\t\t重新获得信息")
        app.logger.debug(f"\t\t排序信息:{sort}")
    else:
        sort = (None, None) 
    

    # 从数据库读取对应表格
    role  = ("管理员") if Database_Utils.user.check_admin(session['operator_name']) else ("普通用户")
    timer = debugTimer(f"开始获取表格 (用户:{session['operator_name']}, 权限: {role})", "获取表格完毕")
    timer.start()
    # 生成查询问句
    if(Database_Utils.user.check_admin(session['operator_name'])):row_query = {}
    else:row_query = {'data.行号': {'$in': authorized_rows}}
    # 尝试获取数据（如果不存在数据则会抛出RuntimeError错误）
    try: 
        table_data = Database_Utils.table.load_table(tb_name=table_name, search_query=row_query, sort=sort)
    except RuntimeError as e: 
        app.logger.debug(f"\t\t{e}")
        emptyTable_json = dict({})
        table_data = TableData(json=emptyTable_json, tb_name=table_show)
    timer.end()


    # 处理获得的文档成为可被Juinja2渲染的格式
    for i in range(len(table_data.rows)):
        # if(table_data.rows[i][authorization_inedx] in authorized_rows) or (Database_Utils.user.check_admin(session['operator_name'])):
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

    count = len(data)
    data = data[start:end]
    return {"code":code, "msg":msg, "count":count, "data":data}

# 主界面 - 数据接口
@app.route('/api/dataMain/<string:option>')
def apiData_dataMain(option):

    """
    option: normal 或 archived 

    主界面表格的数据接口，返回数据包括了
    {
        code = xx,                          # 0 means success 
        msg  = yy,                          # message for debug purpose
        count = zz,                         # 总行数（被layui用于分页使用）
        data  = [
            {
               tb_name : XX,                # 表格名称
               upload_operator : XX         # 指示 - 提交人
               upload_time : XX             # 指示 - 提交时间
               due : XX                     # 指示 - 截止日期
               count_completed : XX         # 完成度 - 完成行数
               count_uncompleted : XX       # 完成度 - 未完成行数
               count_total : XX             # 完成度 - 全部行数
               percentage : XX              # 完成度 - 百分比/小数
               url_edit : XX                # 操作按钮URL - 查看填写表单
               url_edit_mustFill X XX       # 操作按钮URL - 编辑必填值
               url_edit_dueNComment : XX    # 操作按钮URL - 编辑填报说明/截止时期
               url_delete : XX              # 操作按钮URL - 删除表单
            },
            ...
        ]
    }
    """
    app.logger.info('正在访问主界面数据接口')

    # 获取 请求类型
    if(option == 'archived'):archive_query = {'archived':''}
    else:archive_query = {'archived':None}

    # 获取 分页请求
    page  = int(request.args['page'])
    limit = int(request.args['limit'])
    start = (page - 1) * limit

    # 获取 查询请求
    partial_tb_name = request.args.get('partial_tb_name')
    if(partial_tb_name is not None): tb_query = {'tb_name':{"$regex":partial_tb_name}}
    else: tb_query = {}

    # 返回的数据
    rtn_data = {
        'code'  : 0,
        'msg'   : "",
        'count' : 0,
        'data'  : []
    }

    # 使用其中一列进行排序
    sort = (None,None)
    if('field' not in dict(request.args).keys()): 
        sort = ('tb_name',+1) # 默认使用提交时间排序
    else:
        key   =  request.args.get('field')
        order = (-1) if(request.args.get('order') == 'desc') else (1)
        sort  = (key, order)
        app.logger.debug(f"\t\t重新获得信息")
        app.logger.debug(f"\t\t排序信息:{sort}")
        pass 

    
    # 通过meta确认，仅在当前页显示的表单（通过XX排序）
    # 尝试获取数据（如果不存在数据则会抛出RuntimeError错误）
    try: 

        # ======================================================================
        # TODO: IMPLMENT METHOD SUCH THAT THIS LIMIT AND SKIP WORKS AS YOU EXPECTED
        # ======================================================================
        # table_data = Database_Utils.meta.pull_tableMeta_s(sort=sort)
        search_query = {}
        search_query.update(tb_query)
        search_query.update(archive_query)
        table_data = Database_Utils.meta.pull_tableMeta_s(sort=sort, limit=limit, skip=start, search_query=search_query)
        rtn_data['count'] = Database_Utils.stat.get_table_count(search_query=search_query)

        tb_names = [table_i['tb_name'] for table_i in table_data]
    except RuntimeError as e: 
        app.logger.debug(f"\t\t{e}")
        tb_names = []
    
    # 处理每张表格得到想要的信息
    for tb_name in tb_names:  
        cur_table_data = {}
        table_meta = Database_Utils.meta.load_tablemMeta(tb_name=tb_name)
        meta_preserveKey = [
            'tb_name'           # 表格名称
            ,'upload_operator'  # 指示 - 提交人
            ,'upload_time'      # 指示 - 提交时间
            ,'due'              # 指示 - 截止日期
        ]
        cur_table_data = {i:table_meta[i] for i in meta_preserveKey}
        completion_state      = Database_Utils.stat.completion(tb_name=tb_name, 
            is_admin=Database_Utils.user.check_admin(session['operator_name']), 
            authorized_banknos=Database_Utils.user.get_rows(session['operator_name']))
        cur_table_data['count_total']       = completion_state['total']             # 完成度 - 完成行数
        cur_table_data['count_completed']   = completion_state['completed']         # 完成度 - 未完成行数
        cur_table_data['count_uncompleted'] = completion_state['uncompleted']       # 完成度 - 全部行数
        cur_table_data['percentage']    = completion_state['percentage']            # 完成度 - 百分比
        cur_table_data['url_edit']              = url_for('edit_specified_table',table_name=tb_name)
        cur_table_data['url_edit_mustFill']     = url_for('select_RequredAttribute', tb_name=tb_name, return_aftFinish=True)
        cur_table_data['url_edit_dueNComment']  = url_for('fill_dueDate_n_comment', tb_name=tb_name)
        cur_table_data['url_delete']            = url_for('table_clear', table_name=tb_name)
        rtn_data['data'].append(cur_table_data)


    return rtn_data

# AJAX提交请求 - 提交普通单元格
@app.route('/api/submit_row',methods=["POST"])
def submit_specified_tableRow():
    """
    接受Ajax POST上传请求的路由, 更新数据库中特定集合(对应表格)的特定文件(对应行)
    """

    _id        = request.form.get('_id')
    table_name = request.form.get('table_name')
    req_data   = dict(request.form)
    op_name = session['operator_name']
    op_time = gen_dateTime_str()

    app.logger.info('提交普通单元格, _id:' + _id)

    # DEBUG LOGGGING 
    # debug_string = f""" 
    # Saving changes for
    #   table  = {table_name}
    #   row_id = {_id}
    #   data   = {req_data}

    # Action performed by
    #   user = {op_name}
    #   time = {op_time}
    # """
    # app.logger.debug(debug_string)
    origi_document = Database_Utils.row.get_table_row(table_name=table_name, row_id=_id)
    modif_document = origi_document.copy()
    for title,cell_data in origi_document['data'].items():
        modif_data = req_data[title] 
        if isinstance(modif_data, list): modif_data = modif_data[0]
        modif_document['data'][title] = modif_data
    modif_document['user']['name'] = op_name
    modif_document['user']['time'] = op_time


    timer = debugTimer("开始上传行变更", "行变更上传完毕")
    timer.start()
    Database_Utils.row.set_table_row(table_name=table_name, row_id=_id, data=modif_document)
    timer.end()

    origi_document = Database_Utils.row.get_table_row(table_name=table_name, row_id=_id)

    return "Success !"

# 点击多选单元格跳出的选项
@app.route('/multiChoice/<string:tb_name>/<string:title>/<string:_id>')
def edit_multiChoice(tb_name,title, _id):
    meta = Database_Utils.meta.load_tablemMeta(tb_name=tb_name)
    options = meta['option_optionDict'][title]
    app.logger.info(f"正在编辑预设单元格, table:{tb_name}, title:{title}, _id:{_id}, ")
    return render_template('table_show_multiChoice.html',
        tb_name     = tb_name,
        title       = title,
        _id         = _id,
        options     = options,
        submit_url  = url_for('submit_mulitiChoise')
    )

# AJAX提交请求 - 提交多选单元格选项
@app.route('/submit_multiChoice', methods=['GET'])
def submit_mulitiChoise():
    op_name = session['operator_name']
    op_time = gen_dateTime_str()

    table_name  = request.args.get("tb_name")
    choice_title= request.args.get("title")
    _id         = request.args.get("_id")
    choice      = request.args.get("choice")

    modif_document = Database_Utils.row.get_table_row(table_name=table_name, row_id=_id)
    print(modif_document)
    modif_document['data'][choice_title] = choice
    modif_document['user']['name'] = op_name
    modif_document['user']['time'] = op_time
    Database_Utils.row.set_table_row(table_name=table_name, row_id=_id, data=modif_document)

    app.logger.info(f"提交预设单元格, table:{table_name}, title:{choice_title}, choice:{choice}, _id:{_id}")
    return redirect(url_for('edit_specified_table', table_name=table_name))

# 删除表格
@app.route('/api/delete_table', methods=['GET'])
def delete_specified_table_api():
    table_name = request.args.get('tb_name') 
    app.logger.debug(f'\t\t正在删除表单：{table_name}')
    config=DB_Config()
    db = MongoDatabase()
    db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
    db.drop(collection = table_name)
    db.close()
    Database_Utils.meta.del_tablemMeta(tb_name=table_name)
    app.logger.debug(f'\t\t表单：{table_name} 删除成功')

    app.logger.info(f"删除表单, table:{table_name}")
    return "Delete Successful !"

# (DEPRECATED) 归档表格（标记其元数据为已经归档）
@app.route('/api/archive_table', methods=['GET'])
def archive_specified_table_api():
    tb_name = request.args.get('tb_name')
    app.logger.debug(f'\t\t正在标记表单：{tb_name} 为归档文件')
    meta = Database_Utils.meta.load_tablemMeta(tb_name=tb_name)
    meta['archived'] = ""
    Database_Utils.meta.save_tablemMeta(tb_name=tb_name, meta=meta)
    app.logger.debug(f'\t\归档表单：{tb_name} 标记成功')
    return "Archive Successful"

# (DEPRECATED) 去除归档标记
@app.route('/api/unarchive_table', methods=['GET'])
def unarchive_specified_table_api():
    tb_name = request.args.get('tb_name')
    app.logger.debug(f'\t\t正在标记表单：{tb_name} 为非归档文件')
    meta = Database_Utils.meta.load_tablemMeta(tb_name=tb_name)
    if('archived' in meta.keys()): del meta['archived']
    Database_Utils.meta.save_tablemMeta(tb_name=tb_name, meta=meta)
    app.logger.debug(f'\t\非归档表单：{tb_name} 标记成功')
    return "Unarchive Successful"

# 切换归档（如果已经归档标记为未归档，反之亦然）
@app.route('/api/toggle_archive', methods=['GET'])
def toggle_archive_specified_table_api():
    tb_name = request.args.get('tb_name')
    temp_meta = Database_Utils.meta.load_tablemMeta(tb_name=tb_name)

    if('archived' in temp_meta.keys()): 
        app.logger.debug(f'\t\t正在取消表单：{tb_name} 的归档标记')
        del temp_meta['archived']
        app.logger.debug(f'\t\t归档表单：{tb_name} 已被取消归档')
    else:
        app.logger.debug(f'\t\t正在给未归档表单：{tb_name} 添加标记')
        temp_meta['archived'] = ""
        app.logger.debug(f'\t\t未归档表单：{tb_name} 已被归档')

    Database_Utils.meta.del_tablemMeta(tb_name=tb_name)
    Database_Utils.meta.save_tablemMeta(tb_name=tb_name, meta=temp_meta)
    return "Toggle Successful !"

# 模版页面渲染 - 主界面
@app.route('/main')
def show_all_tables_mainPage():
    app.logger.info('进入渲染主界面')
    return render_template('table_show_main_new.html'
        ,is_admin = Database_Utils.user.check_admin(session['operator_name']))

# 模版页面渲染  - 编辑界面
@app.route('/edit/<string:table_name>')
def edit_specified_table(table_name):
    app.logger.info(f'进入编辑主界面, table:{table_name}')

    show_operator        = True   # 是否展示操作员信息
    authorization_inedx  = 0      # 用于确认用户权限的列的序号 (这里 0 指的是 ‘行号’ 在标题的第一个位置)

    # ========================================
    # 设置行属性 
    column_titles = Database_Utils.table.get_tableTitles(table_name) 
    is_admin       = Database_Utils.user.check_admin(session['operator_name'])
    auth_rows      = Database_Utils.user.get_rows(session['operator_name'])
    count_authRows = Database_Utils.stat.count_allRows(tb_name=table_name, is_admin=is_admin, authorized_banknos=auth_rows)

    if(show_operator): column_titles += TableData.operator_titles
    # (这里的id:title映射将被Jinja2赋值到 layui数据表单中的 每行的field上)
    column_ids    = [i for i in column_titles]
    column_dict   = {column_ids[i]:column_titles[i] for i in range(len(column_titles))}

    # 使用模版渲染表格
    table_meta = Database_Utils.meta.load_tablemMeta(tb_name=table_name)
    if('comment' in table_meta.keys()): comment = table_meta['comment']
    else:                               comment = "提交人暂时还未填写说明"
    if(comment==""):                    comment = "提交人暂时还未填写说明"

    # ========================================
    # 如果是第一次打开
    if(request.args.get('entry') == "main_page"): first_entry = True
    else: first_entry = False

    return render_template(
        'table_show_edit.html',\
        column_dict         = column_dict,\
        table_name          = table_name, \
        authorization_title = column_titles[authorization_inedx], \
        operator_title      = TableData.operator_titles,\
        table_meta          = table_meta,\
        number_of_rows      = count_authRows,\
        comment             = comment,
        first_entry         = first_entry
        )

