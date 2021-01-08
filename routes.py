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
                                                    # 未知上传方法 (GET及其他)
        return render_template("redirect_fileUploaded.html",\
            message=f"上传文件失败, 错误: 位置上传方法 (需要为POST)")









@app.route('/data/all', methods=["POST", "GET"])
def export_table(): 
    """
    数据接口
    """
    code  = 0  # 0 means success
    msg   = ""
    count = 1000
    data = []
    
    # Process for data
    table_name = 'Madness'
    table_data = Database_Utils.load_table(table_name)
    for i in range(len(table_data.rows)):
        temp = {}
        _id  = table_data.ids[i]
        temp['_id'] = _id
        _row = table_data.rows[i]
        for j in range(len(table_data.titles)):
            _cell  =_row[j]
            _title =  table_data.titles[j]
            temp[_title] = _cell
        data.append(temp)
    
    return {"code":code, "msg":msg, "count":count, "data":data}


    data = {"code":0,"msg":"","count":1000,"data":[
                {"ID":10000,"用户名":"user-0","性别":"女","城市":"城市-0","签名":"签名-0","积分":255,"评分":24,"财富":82830700,"职业":"作家","积分":57},
                {"ID":10001,"用户名":"user-1","性别":"男","城市":"城市-1","签名":"签名-1","积分":884,"评分":58,"财富":64928690,"职业":"词人","积分":27},{"ID":10002,"用户名":"user-2","性别":"女","城市":"城市-2","签名":"签名-2","积分":650,"评分":77,"财富":6298078,"职业":"酱油","积分":31},{"ID":10003,"用户名":"user-3","性别":"女","城市":"城市-3","签名":"签名-3","积分":362,"评分":157,"财富":37117017,"职业":"诗人","积分":68},{"ID":10004,"用户名":"user-4","性别":"男","城市":"城市-4","签名":"签名-4","积分":807,"评分":51,"财富":76263262,"职业":"作家","积分":6},{"ID":10005,"用户名":"user-5","性别":"女","城市":"城市-5","签名":"签名-5","积分":173,"评分":68,"财富":60344147,"职业":"作家","积分":87},{"ID":10006,"用户名":"user-6","性别":"女","城市":"城市-6","签名":"签名-6","积分":982,"评分":37,"财富":57768166,"职业":"作家","积分":34},{"ID":10007,"用户名":"user-7","性别":"男","城市":"城市-7","签名":"签名-7","积分":727,"评分":150,"财富":82030578,"职业":"作家","积分":28},{"ID":10008,"用户名":"user-8","性别":"男","城市":"城市-8","签名":"签名-8","积分":951,"评分":133,"财富":16503371,"职业":"词人","积分":14},{"ID":10009,"用户名":"user-9","性别":"女","城市":"城市-9","签名":"签名-9","积分":484,"评分":25,"财富":86801934,"职业":"词人","积分":75},{"ID":10010,"用户名":"user-10","性别":"女","城市":"城市-10","签名":"签名-10","积分":1016,"评分":182,"财富":71294671,"职业":"诗人","积分":34},{"ID":10011,"用户名":"user-11","性别":"女","城市":"城市-11","签名":"签名-11","积分":492,"评分":107,"财富":8062783,"职业":"诗人","积分":6},{"ID":10012,"用户名":"user-12","性别":"女","城市":"城市-12","签名":"签名-12","积分":106,"评分":176,"财富":42622704,"职业":"词人","积分":54},{"ID":10013,"用户名":"user-13","性别":"男","城市":"城市-13","签名":"签名-13","积分":1047,"评分":94,"财富":59508583,"职业":"诗人","积分":63},{"ID":10014,"用户名":"user-14","性别":"男","城市":"城市-14","签名":"签名-14","积分":873,"评分":116,"财富":72549912,"职业":"词人","积分":8},{"ID":10015,"用户名":"user-15","性别":"女","城市":"城市-15","签名":"签名-15","积分":1068,"评分":27,"财富":52737025,"职业":"作家","积分":28},{"ID":10016,"用户名":"user-16","性别":"女","城市":"城市-16","签名":"签名-16","积分":862,"评分":168,"财富":37069775,"职业":"酱油","积分":86},{"ID":10017,"用户名":"user-17","性别":"女","城市":"城市-17","签名":"签名-17","积分":1060,"评分":187,"财富":66099525,"职业":"作家","积分":69},{"ID":10018,"用户名":"user-18","性别":"女","城市":"城市-18","签名":"签名-18","积分":866,"评分":88,"财富":81722326,"职业":"词人","积分":74},{"ID":10019,"用户名":"user-19","性别":"女","城市":"城市-19","签名":"签名-19","积分":682,"评分":106,"财富":68647362,"职业":"词人","积分":51},{"ID":10020,"用户名":"user-20","性别":"男","城市":"城市-20","签名":"签名-20","积分":770,"评分":24,"财富":92420248,"职业":"诗人","积分":87},{"ID":10021,"用户名":"user-21","性别":"男","城市":"城市-21","签名":"签名-21","积分":184,"评分":131,"财富":71566045,"职业":"词人","积分":99},{"ID":10022,"用户名":"user-22","性别":"男","城市":"城市-22","签名":"签名-22","积分":739,"评分":152,"财富":60907929,"职业":"作家","积分":18},{"ID":10023,"用户名":"user-23","性别":"女","城市":"城市-23","签名":"签名-23","积分":127,"评分":82,"财富":14765943,"职业":"作家","积分":30},{"ID":10024,"用户名":"user-24","性别":"女","城市":"城市-24","签名":"签名-24","积分":212,"评分":133,"财富":59011052,"职业":"词人","积分":76},{"ID":10025,"用户名":"user-25","性别":"女","城市":"城市-25","签名":"签名-25","积分":938,"评分":182,"财富":91183097,"职业":"作家","积分":69},{"ID":10026,"用户名":"user-26","性别":"男","城市":"城市-26","签名":"签名-26","积分":978,"评分":7,"财富":48008413,"职业":"作家","积分":65},{"ID":10027,"用户名":"user-27","性别":"女","城市":"城市-27","签名":"签名-27","积分":371,"评分":44,"财富":64419691,"职业":"诗人","积分":60},{"ID":10028,"用户名":"user-28","性别":"女","城市":"城市-28","签名":"签名-28","积分":977,"评分":21,"财富":75935022,"职业":"作家","积分":37},{"ID":10029,"用户名":"user-29","性别":"男","城市":"城市-29","签名":"签名-29","积分":647,"评分":107,"财富":97450636,"职业":"酱油","积分":27}]}
    # data = {"code":0,"msg":"","count":1000,"data":[{"id":10000,"username":"user-0","sex":"女","city":"城市-0","sign":"签名-0","experience":255,"logins":24,"wealth":82830700,"classify":"作家","score":57},{"id":10001,"username":"user-1","sex":"男","city":"城市-1","sign":"签名-1","experience":884,"logins":58,"wealth":64928690,"classify":"词人","score":27},{"id":10002,"username":"user-2","sex":"女","city":"城市-2","sign":"签名-2","experience":650,"logins":77,"wealth":6298078,"classify":"酱油","score":31},{"id":10003,"username":"user-3","sex":"女","city":"城市-3","sign":"签名-3","experience":362,"logins":157,"wealth":37117017,"classify":"诗人","score":68},{"id":10004,"username":"user-4","sex":"男","city":"城市-4","sign":"签名-4","experience":807,"logins":51,"wealth":76263262,"classify":"作家","score":6},{"id":10005,"username":"user-5","sex":"女","city":"城市-5","sign":"签名-5","experience":173,"logins":68,"wealth":60344147,"classify":"作家","score":87},{"id":10006,"username":"user-6","sex":"女","city":"城市-6","sign":"签名-6","experience":982,"logins":37,"wealth":57768166,"classify":"作家","score":34},{"id":10007,"username":"user-7","sex":"男","city":"城市-7","sign":"签名-7","experience":727,"logins":150,"wealth":82030578,"classify":"作家","score":28},{"id":10008,"username":"user-8","sex":"男","city":"城市-8","sign":"签名-8","experience":951,"logins":133,"wealth":16503371,"classify":"词人","score":14},{"id":10009,"username":"user-9","sex":"女","city":"城市-9","sign":"签名-9","experience":484,"logins":25,"wealth":86801934,"classify":"词人","score":75},{"id":10010,"username":"user-10","sex":"女","city":"城市-10","sign":"签名-10","experience":1016,"logins":182,"wealth":71294671,"classify":"诗人","score":34},{"id":10011,"username":"user-11","sex":"女","city":"城市-11","sign":"签名-11","experience":492,"logins":107,"wealth":8062783,"classify":"诗人","score":6},{"id":10012,"username":"user-12","sex":"女","city":"城市-12","sign":"签名-12","experience":106,"logins":176,"wealth":42622704,"classify":"词人","score":54},{"id":10013,"username":"user-13","sex":"男","city":"城市-13","sign":"签名-13","experience":1047,"logins":94,"wealth":59508583,"classify":"诗人","score":63},{"id":10014,"username":"user-14","sex":"男","city":"城市-14","sign":"签名-14","experience":873,"logins":116,"wealth":72549912,"classify":"词人","score":8},{"id":10015,"username":"user-15","sex":"女","city":"城市-15","sign":"签名-15","experience":1068,"logins":27,"wealth":52737025,"classify":"作家","score":28},{"id":10016,"username":"user-16","sex":"女","city":"城市-16","sign":"签名-16","experience":862,"logins":168,"wealth":37069775,"classify":"酱油","score":86},{"id":10017,"username":"user-17","sex":"女","city":"城市-17","sign":"签名-17","experience":1060,"logins":187,"wealth":66099525,"classify":"作家","score":69},{"id":10018,"username":"user-18","sex":"女","city":"城市-18","sign":"签名-18","experience":866,"logins":88,"wealth":81722326,"classify":"词人","score":74},{"id":10019,"username":"user-19","sex":"女","city":"城市-19","sign":"签名-19","experience":682,"logins":106,"wealth":68647362,"classify":"词人","score":51},{"id":10020,"username":"user-20","sex":"男","city":"城市-20","sign":"签名-20","experience":770,"logins":24,"wealth":92420248,"classify":"诗人","score":87},{"id":10021,"username":"user-21","sex":"男","city":"城市-21","sign":"签名-21","experience":184,"logins":131,"wealth":71566045,"classify":"词人","score":99},{"id":10022,"username":"user-22","sex":"男","city":"城市-22","sign":"签名-22","experience":739,"logins":152,"wealth":60907929,"classify":"作家","score":18},{"id":10023,"username":"user-23","sex":"女","city":"城市-23","sign":"签名-23","experience":127,"logins":82,"wealth":14765943,"classify":"作家","score":30},{"id":10024,"username":"user-24","sex":"女","city":"城市-24","sign":"签名-24","experience":212,"logins":133,"wealth":59011052,"classify":"词人","score":76},{"id":10025,"username":"user-25","sex":"女","city":"城市-25","sign":"签名-25","experience":938,"logins":182,"wealth":91183097,"classify":"作家","score":69},{"id":10026,"username":"user-26","sex":"男","city":"城市-26","sign":"签名-26","experience":978,"logins":7,"wealth":48008413,"classify":"作家","score":65},{"id":10027,"username":"user-27","sex":"女","city":"城市-27","sign":"签名-27","experience":371,"logins":44,"wealth":64419691,"classify":"诗人","score":60},{"id":10028,"username":"user-28","sex":"女","city":"城市-28","sign":"签名-28","experience":977,"logins":21,"wealth":75935022,"classify":"作家","score":37},{"id":10029,"username":"user-29","sex":"男","city":"城市-29","sign":"签名-29","experience":647,"logins":107,"wealth":97450636,"classify":"酱油","score":27}]}
    return data


@app.route('/debug')
def debug_function_here_QAQ():
    table_name = 'Madness'
    column_titles = Database_Utils.get_tableTitles(table_name)
    column_ids    = [i for i in column_titles]
    column_dict   = {column_ids[i]:column_titles[i] for i in range(len(column_titles))}


    return render_template('table_show_edit.html', column_dict=column_dict)

    column_titles = ["_id","ID","用户名","性别","城市","签名","积分","评分","职业","财富"]
    column_ids    = [i for i in column_titles]
    column_dict   = {column_ids[i]:column_titles[i] for i in range(len(column_titles))}
    return render_template('table_show_edit.html', \
        column_dict     = column_dict,   \
        # column_titles = column_titles, \
        # column_ids    = column_ids,    \
    )










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
        logging.warn("WARNING, User attempts to access URL with an invalid table option .")
        abort(404)
