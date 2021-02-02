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
from flask                  import Flask, config, render_template, flash, make_response, send_from_directory, redirect, url_for, session, request
from routes_utils           import *
from routes_file            import *
from debugTimer             import *
from routes_table_static    import *


# =============================================
# 自动渲染表格 - 上传文件

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


# =============================================
# 自动渲染表格 - 数据接口

# DEPRECATED
# @app.route('/data_all/<string:table_name>')
# def export_table_data_all(table_name):
    # """
    # 数据接口
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

# 编辑页面
@app.route('/api/dataEdit')
def apiData_dataEdit(): 
    """
    获取”编辑页面“的表格的数据接口
    """
    # 获取 表格信息
    table_name = request.args['tb_name']

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

# 主界面
@app.route('/api/dataMain')
def apiData_dataMain():

    """
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
    # 获取 分页请求
    page  = int(request.args['page'])
    limit = int(request.args['limit'])
    start = (page - 1) * limit

    # 返回的数据
    rtn_data = {
        'code'  : 0,
        'msg'   : "",
        'count' : Database_Utils.meta.get_tableMeta_count(),
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
        table_data = Database_Utils.meta.pull_tableMeta_s(sort=sort)

        # ======================================================================
        # TODO: IMPLMENT METHOD SUCH THAT THIS LIMIT AND SKIP WORKS AS YOU EXPECTED
        # ======================================================================
        table_data = Database_Utils.meta.pull_tableMeta_s(sort=sort, limit=limit, skip=start)

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
        completion_state      = Database_Utils.stat.completion(tb_name=tb_name)
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

# =============================================
# 自动渲染表格 - 展示表格/提交变更 

# 主界面
@app.route('/demo')
def show_all_tables_mainPage():
    print('=====')
    print(session['operator_name'])
    print(Database_Utils.user.check_admin(session['operator_name']))

    return render_template('table_show_main_new.html'
        ,is_admin = Database_Utils.user.check_admin(session['operator_name'])
    )

# 编辑界面
@app.route('/edit/<string:table_name>')
def edit_specified_table(table_name):

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

# =============================================
# 提交变更 
# 自动渲染表格 - 提交普通单元格

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

    return render_template('table_show_multiChoice.html',
        tb_name     = tb_name,
        title       = title,
        _id         = _id,
        options     = options,
        submit_url  = url_for('submit_mulitiChoise')
    )

# 提交多选单元格选项
@app.route('/submit_multiChoice')
def submit_mulitiChoise():
    op_name = session['operator_name']
    op_time = gen_dateTime_str()

    table_name  = request.args.get("tb_name")
    choice_title= request.args.get("title")
    _id         = request.args.get("_id")
    choice      = request.args.get("choice")
    print('=' * 80)
    print(_id, table_name, choice_title, choice)

    modif_document = Database_Utils.row.get_table_row(table_name=table_name, row_id=_id)
    print(modif_document)
    modif_document['data'][choice_title] = choice
    modif_document['user']['name'] = op_name
    modif_document['user']['time'] = op_time
    Database_Utils.row.set_table_row(table_name=table_name, row_id=_id, data=modif_document)

    return redirect(url_for('edit_specified_table', table_name=table_name))

