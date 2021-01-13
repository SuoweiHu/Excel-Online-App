# Some built-int modules
# import json
# import logging
# import os
# import sys
# import pprint
# import datetime
# import random

# from modules._Database  import MongoDatabase, DB_Config
# from modules._TableData import TableData
# from modules._ExcelVisitor import ExcelVisitor
# from modules._JsonVisitor  import JSON
# from modules._Redis import RedisCache
import flask
from modules._Database_Utils import Database_Utils
from modules._Hash_Utils import hash_id
from routes_table import *
from routes_file  import *


# from pymongo.periodic_executor import _on_executor_deleted
# from werkzeug   import utils
from app import app
# from json2html  import json2html
from flask      import Flask, abort, config, render_template, flash, make_response, send_from_directory, redirect, url_for, session, request

# =============================================

@app.route('/', methods=["POST","GET"])
def initialize():
    """
    初始化所有信息
    """
    session['login_state']   = False
    session['operator']      = None
    session['operator_name'] = None
    session['previous_page'] = None
    session['page']          = 0
    return redirect(url_for('index'))

@app.route('/index')
def index():
    """
    如果为登陆跳转到登陆页面, 否则进入展示所有表格的页面
    """
    if(not session['login_state']):return render_template('index_logged_out.html')
    else:return redirect('/table/all')

@app.route('/login', methods=["POST"])
def login():
    """
    上传登陆账号与密码校验, 返回登陆成功与否信息, 跳转回主界面
    """
    name    = request.form["operator_name"]
    password = request.form["operator_pass"]
    check_login = Database_Utils.check_password(name, password)

    # 对比数据库中的密码
    if(check_login):
        session['login_state']   = True
        session['operator']      = name
        session['operator_name'] = name
        return render_template("redirect_login.html", message=f"登陆成功: 用户名为[ {name} ]")
    else: 
        return render_template("redirect_login.html", message="登陆失败: 账号或密码不匹配")

# =============================================

@app.route('/redirect', methods=["POST","GET"])
def redirect_to_index():
    """
    跳转到主页面, 或者指定页面
    """
    if(session['previous_page'] is None):
        return redirect(url_for('index'))
    else:
        prev_page = session['previous_page']
        session['previous_page'] = None
        return redirect(prev_page)

# =============================================

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
    authorized_rows      = Database_Utils.get_rows(session['operator_name'])
    authorized_rows      = [str(i) for i in authorized_rows]
    

    # ========================================
    # Layui数据接口 默认返回属性
    code  = 0  # 0 means success
    msg   = ""
    count = 1000
    data = []

    # 从数据库读取对应表格
    table_data = Database_Utils.load_table(table_name)
    for i in range(len(table_data.rows)):
        if(table_data.rows[i][authorization_inedx] in authorized_rows) or (Database_Utils.check_admin(session['operator_name'])):
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
    column_titles = Database_Utils.get_tableTitles(table_name) 
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

    origi_document = Database_Utils.get_table_row(table_name=table_name, row_id=_id)
    modif_document = origi_document.copy()
    for title,cell_data in origi_document['data'].items():
        modif_data = req_data[title] 
        if isinstance(modif_data, list): modif_data = modif_data[0]
        modif_document['data'][title] = modif_data
    modif_document['user']['name'] = op_name
    modif_document['user']['time'] = op_time
    Database_Utils.set_table_row(table_name=table_name, row_id=_id, data=modif_document)
    origi_document = Database_Utils.get_table_row(table_name=table_name, row_id=_id)

    return "Success !"


# =============================================

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
        op_rows = Database_Utils.get_rows(op_name)  # 提取用户允许访问的行
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
