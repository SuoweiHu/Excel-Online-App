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
from routes_table import *


# from pymongo.periodic_executor import _on_executor_deleted
# from werkzeug   import utils
from app import app
from json2html  import json2html
from flask      import Flask, config, render_template, flash, make_response, send_from_directory, redirect, url_for, session, request


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
    if(session['previous_page'] is None):return redirect(url_for('index'))
    else:
        prev_page = session['previous_page']
        session['previous_page'] = None
        return redirect(prev_page)


@app.route('/file', methods=["POST"])
def upload_file():
    """
    上传文件, 跳转到中介页面显示 “上传成功/失败”, 然后进入该表格的展示页面/ 回到主界面
    """
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

            # Read from Excel file 
            tb_name = f_name
            excelReader = ExcelVisitor(f'./src/temp/{f_name}')
            titles      = excelReader.get_titles()
            info_table  = excelReader.get_infoTable()
            oper_table  = excelReader.get_operTable()
            os.remove(f'./src/temp/{f_name}')# 读取后删除文件
            ids_list    = [hash_id(str(random.random())) for i in range(len(info_table))]

            # Store to custom class format 
            tableData = TableData(json=None, tb_name=tb_name, titles=titles, rows=info_table, operators=oper_table, ids=ids_list)
            tableData_Json = tableData.toJson()
            if(save_json): JSON.save(tableData_Json, JSON.PATH+f"{tb_name}.json") # 如果想暂时存储为JSON文件预览
            Database_Utils.upload_table(tb_name.split('.')[0],tableData_Json)

            return render_template("redirect_fileUploaded.html", message=f"成功上传文件, 文件名: {f_name}", table_name = f_name)

    # 未知上传方法 (GET及其他)
    else:
            return render_template("redirect_fileUploaded.html", message=f"上传文件失败, 错误: 位置上传方法 (需要为POST)")


# =============================================

@app.route('/table/<string:option>', methods=["GET", "POST"])
def table(option):
    """
    根据不同的option跳转到不同的填表/展示页面
    """
    # 检测登陆状态, 如果为登陆则返回登陆界面
    if(session['operator'] is None) and (session['operator_name'] is None):
        return render_template('redirect_prompt.html')

    # 如果option为all: 跳转到用户选择表格界面
    if(option=='all'):
        cur=request.args.get('curr')
        limit=request.args.get('limit')
        user=session["operator_name"]
        return table_all(cur, limit, user)

    # 如果option为clear: 清除特定表单的数据
    elif(option=='clear'):
        table_name = request.args.get('table_name')
        table_name = table_name.replace(' ', '')
        table_name = table_name.split('.')[0] # 去除xlsx文件后缀
        return table_clear(table_name=table_name)

    # 如果options为show: 用户选择(多)行/预览界面
    elif(option=='show'):
        # 提取表名
        tb_name = request.args.get('table_name')
        # 提取用户允许访问的行
        op_name = session["operator_name"]
        op_rows = Database_Utils.get_rows(op_name)
        return table_show(table_name=tb_name, show_rows_of_keys=op_rows, user=op_name) 

    # 如果options为表格名: 用户编辑行界面
    elif(option=='edit'):
        # 提取表名 / 行号
        tb_name = request.args.get('table_name')
        row_id  = request.args.get('row_id')
        return table_edit(table_name=tb_name, edit_row_key=row_id)
        # 不通过入参提取表明, 直接显示用户有权限访问的所有表单
    
    # 如果option为submit: 提交数据然后返回show界面 (POST)
    elif(option=='submit'):
        table_name  = request.form.get('table_name')
        row_id      = request.form.get('row_id')
        return table_submit(table_name=table_name, row_id=row_id, user=session["operator_name"])
