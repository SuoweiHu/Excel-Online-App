from flask      import Flask, render_template, flash, make_response, send_from_directory, redirect, url_for, session, request
from _Database  import MongoDatabase
from _TableData import TableData
from _ExcelVisitor import ExcelVisitor
from _JsonVisitor  import JSON
from _Redis import RedisCache
import sys
import uuid
import hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SAJHDKSAKJDHKJASHKJDKASDD'  
# app.config['MAXs_CONTENT_LENGTH'] = 5 * 1024 * 1024


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

if __name__ == "__main__":

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

    # Try save variable into redis
    r = RedisCache()
    r.start()
    r.save(hash_id(config["tb_name"]), tableData)
    temp_redisLoad = r.load(hash_id(config["tb_name"]))
    JSON.save(temp_redisLoad, JSON.PATH+"temp.json")
    
    sys.exit(0)

    # Store to database
    db = MongoDatabase()
    db.start(host=config['db_host'], port=config['db_port'], name=config['db_name'],clear=True)
    db.insert(collection=config['collection_name'], data=tableDict, _id=hash_id(config["tb_name"]))
    temp_mongoLoad = db.extract(collection=config['collection_name'],_id=hash_id(config["tb_name"]))
    JSON.save(temp_mongoLoad, JSON.PATH+"temp.json")
    db.close()

    sys.exit(0)    

    app.run(host='0.0.0.0', port=5000, debug=True)