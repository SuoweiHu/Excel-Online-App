# Some built-int modules
import os
import sys
import uuid
import hashlib
import pprint
import datetime

# Custom modules
from pymongo.periodic_executor import _on_executor_deleted
from werkzeug import utils
from _Database  import MongoDatabase, Config
from _TableData import TableData
from _ExcelVisitor import ExcelVisitor
from _JsonVisitor  import JSON
from _Redis import RedisCache

# Flask modules
from flask      import Flask, render_template, flash, make_response, send_from_directory, redirect, url_for, session, request

# =============================================
# =============================================
# Flask Application's instance

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SAJHDKSAKJDHKJASHKJDKASDD'  
# app.config['MAXs_CONTENT_LENGTH'] = 5 * 1024 * 1024

# =============================================
# =============================================
# helper functions

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

def hash_id(filename, hash_method=None):
    """
    Generate unique _id in the collection for a given file name 
    filename :: string
    hash_method :: None | "MD5" | "SHA1"
    """
    # # Using uuid method
    # if(hash_method == "MD5"):     return uuid.uuid3(b_filename)
    # elif(hash_method == "SHA1"):  return uuid.uuid5(b_filename)
    # else:                         return uuid.uuid(b_filename)

    # Using hashlib method 
    if(hash_method == "MD5"):       c = hashlib.md5(filename.encode("utf-8"))
    elif(hash_method == "SHA1"):    c = hashlib.sha1(filename.encode("utf-8"))
    else:                           c = hashlib.sha256(filename.encode("utf-8"))
    return c.hexdigest()

# =============================================
# =============================================
# demo functions

def demo_1():
    """
    Demo of following:
        - Using _ExcelVisitor to read from excel file
        - Using _TableData custom type to hold table sheet data 
        - Using _Database to save and read from mongo database
        - Using _Redis to save custom object to database (Failed)
    """
    config=Config(tb_name="2020年二季度.xlsx", db_host='localhost', db_port=27017, db_name="账户统计", collection_name="2020第二季度")
    config={
        "tb_name" : "2020年二季度.xlsx",
        "db_host" : 'localhost',
        "db_port" : 27017,
        "db_name" : "账户统计",
        "collection_name" : "2020第二季度",
    }

    # Read from Excel file 
    tb_name = config["tb_name"]
    excelReader = ExcelVisitor(ExcelVisitor.PATH+tb_name)
    titles      = excelReader.get_titles()
    info_table  = excelReader.get_infoTable()
    oper_table  = excelReader.get_operTable()

    # Store to custom class format 
    tableData = TableData(tb_name=tb_name, titles=titles, rows=info_table, operators=oper_table)
    tableDict = tableData.to_dict()

    # # Try save variable into redis
    # r = RedisCache()
    # r.save(hash_id(config["tb_name"]), tableData)
    # temp_redisLoad = r.load(hash_id(config["tb_name"]))
    # JSON.save(temp_redisLoad, JSON.PATH+"temp.json")

    # Store to database
    db = MongoDatabase()
    db.start(host=config['db_host'], port=config['db_port'], name=config['db_name'],clear=True)
    db.insert(collection=config['collection_name'], data=tableDict, _id=hash_id(config["tb_name"]))
    temp_mongoLoad = db.extract(collection=config['collection_name'],_id=hash_id(config["tb_name"]))
    JSON.save(temp_mongoLoad, JSON.PATH+"temp.json")
    db.close()

    return

# @app.route('/table')
def demo_2():
    """
    Demo of following:
        - Reading from .xlxs file and export to html
        - Flask app (when undesire to run, comment the route decorator)
    """
    config=Config(tb_name="2020年二季度.xlsx")
    config={
        "tb_name" : "2020年二季度.xlsx",
    }

    # Read from Excel file 
    tb_name = config["tb_name"]
    excelReader = ExcelVisitor(ExcelVisitor.PATH+tb_name)
    titles      = excelReader.get_titles()
    info_table  = excelReader.get_infoTable()
    oper_table  = excelReader.get_operTable()

    # Convert the result to html format for printing
    tableData  = TableData(tb_name=tb_name, titles=titles, rows=info_table, operators=oper_table)
    jsonDict   = tableData.to_dict_json2html(show_operator=True)
    htmlString = tableData.to_html(json_dict=jsonDict,show_operator=True)

    # Return html string
    return htmlString

# =============================================
# =============================================
# flask router: main page

@app.route('/', methods=["POST","GET"])
def initialize():
    session['login_state'] = False
    session['operator']    = None
    return redirect(url_for('index'))

@app.route('/redirect', methods=["POST","GET"])
def redirect_to_index():
    return redirect(url_for('index'))

@app.route('/index')
def index():
    if(not session['login_state']==True):
        fileUpload_section = "请登录, 以访问数据库 ... ..."
        insert_section = "请登录, 以访问数据库 ... ..."
        delete_section = "请登录, 以访问数据库 ... ..."
        login_section  = """
            登陆以获得更多权限
            <br>
            <br>
            <form action="/login" method="post">
                账户名:      
                <input type="text" name="operator_name" id=""><br>
                &nbsp;密码:&nbsp;&nbsp;&nbsp; 
                <input type="password" name="operator_pass" id=""><br>
                <br>
                <input type="submit" value="提交">
            </form>
            """
    else:
        fileUpload_section = """
            <form action="/file" method="post" enctype="multipart/form-data">
                <input type="file" name="stuff_file"  id=""><br><br>
                <input type="submit" value="--- 上传 ---">
            </form>
            """
        insert_section = """
            <!---查看特定表单-->
            <form action="/table" method="post">
                更改/查看特定表单:
                <select name="table_name" id="table_name">
                    <option value="2020年一季度.xlsx">2020年一季度.xlsx</option>
                    <option value="2020年二季度.xlsx">2020年二季度.xlsx</option>
                    <option value="2020年三季度.xlsx">2020年三季度.xlsx</option>
                    <option value="2020年四季度.xlsx">2020年四季度.xlsx</option>
                </select>
                <input type="submit" value="确认">
            </form>
            <br>
            """
        delete_section = """
            <!---清除特定表单-->
            <form action="/clear" method="post">
                清除特定表单:
                <select name="table_name" id="table_name">
                    <option value="2020年一季度.xlsx">2020年一季度.xlsx</option>
                    <option value="2020年二季度.xlsx">2020年二季度.xlsx</option>
                    <option value="2020年三季度.xlsx">2020年三季度.xlsx</option>
                    <option value="2020年四季度.xlsx">2020年四季度.xlsx</option>
                </select>
                <input type="submit" value="确认">
            </form>
            <br>

            <!-- 清除所有内容 -->
            <form action="/clear_all" method="post">
                清除所有表单: 
                <input type="submit" value="清除数据库内 所有集合">
            </form>
            """
        login_section = f"""
            --- 已登录 ---
            <br><br>
            <form action="{url_for('initialize')}" method="post">
                <input type="submit" value="退出登录">
            </form>
            """
        

    return render_template('index.html', \
        fileUpload_section = fileUpload_section, \
        insert_section = insert_section, \
        delete_section = delete_section, \
        login_section  = login_section, 
        )

# =============================================
# =============================================
# flask router: table processes

@app.route('/file', methods=["POST"])
def upload_file():
    save_json = False
    save_xlsx = False

    if request.method == "POST":
        # 提取文件名, 若需要使用 save（）方法保存文件 
        f = request.files.get("stuff_file")
        f_name = f.filename
        if('xlsx' not in f_name):
            # 检查文件类型是否正确
            return render_template("upload.html", message=f"上传文件失败, 错误: 文件名后缀为{f_name.split('.')[1]} (需要为xlsx)")
        else: 
            # 保存文件, 从文件读取内容, 并保存到数据库
            f.save(f'./src/temp/{f_name}') # 临时保存文件
            if(save_xlsx): f.save(f'./src/excel/{f_name}') 

            config= Config(f_name=f_name, collection_name=f_name.split('.')[0])
            config={
                "tb_name" : f_name,
                "db_host" : 'localhost',
                "db_port" : 27017,
                "db_name" : "账户统计",
                "collection_name" : f_name.split('.')[0],
            }

            # Read from Excel file 
            tb_name = config["tb_name"]
            excelReader = ExcelVisitor(f'./src/temp/{f_name}')
            titles      = excelReader.get_titles()
            info_table  = excelReader.get_infoTable()
            oper_table  = excelReader.get_operTable()
            os.remove(f'./src/temp/{f_name}')# 读取后删除文件
            

            # Store to custom class format 
            tableData = TableData(tb_name=tb_name, titles=titles, rows=info_table, operators=oper_table)
            tableDict = tableData.to_dict()

            # Store to database
            db = MongoDatabase()
            db.start(host=config['db_host'], port=config['db_port'], name=config['db_name'],clear=False)
            db.insert(collection=config['collection_name'], data=tableDict, _id=hash_id(config['tb_name']))
            temp_mongoLoad = db.extract(collection=config['collection_name'],_id=hash_id(config['tb_name']))
            if(save_json): 
                JSON.save(temp_mongoLoad, JSON.PATH+f"{tb_name}.json") # 如果想暂时存储为JSON文件预览
            db.close()

            return render_template("upload.html", message=f"成功上传文件, 文件名: {f_name}")

    # 未知上传方法 (GET及其他)
    else:
            return render_template("upload.html", message=f"上传文件失败, 错误: 位置上传方法 (需要为POST)")

@app.route('/clear', methods=["POST"])
def clear_db_table():
    config=Config()
    config={
        "db_host" : 'localhost',
        "db_port" : 27017,
        "db_name" : "账户统计",
    }
    table_name = request.form['table_name']
    table_name = table_name.split('.')[0] # 去除xlsx文件后缀
    db = MongoDatabase()
    db.start(host=config['db_host'], port=config['db_port'], name=config['db_name'],clear=False)
    db.drop(collection = table_name)
    db.close()
    return render_template("clear.html", message=f"操作成功: 已清除集合[ {table_name} ]")

@app.route('/clear_all', methods=["POST"])
def clear_database():
    config=Config()
    config={
        "db_host" : 'localhost',
        "db_port" : 27017,
        "db_name" : "账户统计",
    }
    db = MongoDatabase()
    db.start(host=config['db_host'], port=config['db_port'], name=config['db_name'],clear=True)
    db.close()
    return render_template("clear.html", message=f"操作成功: 数据库中所有集合已被清除")

@app.route('/login', methods=["POST"])
def login():
    name = request.form["operator_name"]
    password = request.form["operator_pass"]
    # check_login = check_account_match(name, password) 
    check_login = ('admin' in name) and ('admin' in password)

    # 缺少检测登陆成功的机制
    if(check_login):
        session['login_state'] = True
        session['operator'] = name
        session['operator_name'] = name
        return render_template("login.html", message=f"登陆成功: 用户名为[ {name} ]")
    else: 
        return render_template("login.html", message="登陆失败: 账号或密码不匹配")

@app.route('/table', methods=["POST"])
def table():
    config={
        "tb_name" : "",# 注意这里的文件名是带xlsx后缀的
        "db_host" : 'localhost',
        "db_port" : 27017,
        "db_name" : "账户统计",
        "collection_name" : "",# 这里则 不带xlsx后缀
    }
    config["tb_name"] = request.form['table_name']
    config["collection_name"] = (config["tb_name"]).split('.')[0]

    # Read from Database
    db = MongoDatabase()
    db.start(host=config['db_host'], port=config['db_port'], name=config['db_name'],clear=False)
    temp_mongoLoad = db.extract(collection=config['collection_name'],_id=hash_id(config["tb_name"]))
    db.close()

    # Convert the result to html format for printing
    tableData  = TableData(json=temp_mongoLoad)
    jsonDict   = tableData.to_dict_json2html(show_operator=True)
    htmlString = tableData.to_html(json_dict=jsonDict,show_operator=True)

    # Add form info into string 
    now = datetime.datetime.now()
    day = now.date()
    time = now.time()
    day_str = day.__format__('%Y/%m/%d')
    time_str = time.strftime('%H:%M:%S')
    datetime_str = day_str+ " " + time_str
    print(datetime_str)
    operator_str = session["operator_name"]

    # Return html string rendered by template
    return render_template('table.html', table_info=htmlString, operator_name=operator_str, operator_time=datetime_str)

@app.route('/upload', methods=["POST"])
def upload():
    # User form upload
    form_dict = dict(request.form)

    # Extract Operator Info
    operator = {}
    operator["name"] = form_dict["operator_name"]
    operator["time"] = gen_dateTime_str()   # Use the actual upload time instead
    # operator["time"] = form_dict["operator_time"]

    return "STUFF: " + str(request_dict)

# =============================================
# =============================================
# booter functions

def main():
    app.run(host='0.0.0.0', port=5000, debug=True)
    return

if __name__ == "__main__":
    main()
