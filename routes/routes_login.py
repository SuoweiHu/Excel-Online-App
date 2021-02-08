"""
用户登陆时所用的路由， 包括了：
- '/'               初始化session（登出），然后跳转到登陆页面
- '/index'          若已经登陆跳转至主界面，否则跳转到登陆页面 '/'
- '/login'          登陆界面
- '/api/login'      处理登陆请求
"""

from modules._Database_Utils import Database_Utils
from app import app
from flask      import Flask, abort, config, render_template, flash, make_response, send_from_directory, redirect, url_for, session, request
from .routes_utils import *

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
    user_meta = Database_Utils.user.get_user(name=name)

    # 对比数据库中的密码
    if(check_login):
        session['login_state']   = True
        session['operator']      = name
        session['operator_name'] = name
        session['nickname']      = user_meta['nickname']
        return render_template("redirect_login.html", message=f"欢迎登陆: {session['nickname']} ")
    else: 
        return render_template("redirect_login.html", message="登陆失败: 账号或密码不匹配")

@app.route('/api/login', methods=["GET"])
def api_login_success():
    """
    登陆完成后的接口，传过来的字段有：
    - key_operator_name:        用户ID （例：zhang_san1）
    - key_operator_nickname:    用户中文名（例：张三）可以有重复的名字
    - key_authorized_nums:      用户可操作的行号（例：733101,733102,733121）

    若定义
    - key_operator_name:        logon_usr_id
    - key_operator_nickname:    usr_cn_nm
    - key_authorized_nums:      belg_org_id

    那么最后访问的URL，例如如下：
    /api/login?account=zhang_san1&nickname=张三&auth=733101,733102,733121
    """

    # 请求字段键名
    key_operator_name        = "logon_usr_id"
    key_operator_nickname    = "usr_cn_nm"
    key_authorized_nums      = "belg_org_id"

    # 重置会话
    session.pop('operator')
    session.pop('operator_name')
    session['login_state']   = False
    session['previous_page'] = "/"
    session['page']          = 0
    # 获得参数
    operator_name            = request.args.get(key_operator_name)
    nickname                 = request.args.get(key_operator_nickname)
    authorized_nums          = request.args.get(key_authorized_nums)
    app.logger.debug(f'\t\t正在接入用户')
    app.logger.debug(f'\t\t用户：{operator_name}')
    app.logger.debug(f'\t\t昵称：{nickname}')
    app.logger.debug(f'\t\t权限：{authorized_nums}')
    authorized_nums          = authorized_nums.split(',')
    authorized_nums          = [int(num) for num in authorized_nums]   

    # 存入数据库/会话 + 跳转
    Database_Utils.user.del_user_brutal(name=operator_name)
    Database_Utils.user.add_user(name=operator_name, nickname=nickname, password="",rows=authorized_nums, privilege='generic')
    session['operator']      = session['operator_name'] = operator_name
    session['nickname']      = nickname
    session['login_state']   = True
    return redirect('/table/all')