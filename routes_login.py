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

# from pymongo.periodic_executor import _on_executor_deleted
# from werkzeug   import utils
from app import app
# from json2html  import json2html
from flask      import Flask, abort, config, render_template, flash, make_response, send_from_directory, redirect, url_for, session, request

from routes_utils import *
# from routes_table import *
# from routes_file  import *
# from routes_login import *



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
    check_login = Database_Utils.user.check_password(name, password)

    # 对比数据库中的密码
    if(check_login):
        session['login_state']   = True
        session['operator']      = name
        session['operator_name'] = name
        return render_template("redirect_login.html", message=f"登陆成功: 用户名为[ {name} ]")
    else: 
        return render_template("redirect_login.html", message="登陆失败: 账号或密码不匹配")
