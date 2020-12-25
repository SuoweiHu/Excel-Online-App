from flask import Flask, render_template, flash, make_response, send_from_directory, redirect, url_for, session, request
from Database import Class_MongoDB
from TableData import TableData
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

    tbname = "2020年二季度"
    titles = ["行号","项目号","子账户","账户名","分账户","账户名","受理人","金额"]
    rows   = [["733101","213123","A","XXXX","A1","XXXX","小S",None],
              ["733121","123123","A","XXXX","A1","XXXX","小B","321"],
              ["733131","123123","B","YYYY","B1","YYYY 1",None,"123"],
              ["733141","123123","B","YYYY",None,None,None,"123"],
              ["733151","1231231","B","YYYY","B3","YYYY 3","小B",None]]

    tb_data = TableData(tb_name= tbname, titles=titles, rows=rows)



    print(tb_data.to_dict())

    sys.exit(0)

    db = Class_MongoDB()
    db.start(host='localhost', port=27017, name="NetEase-Music",clear=True)

  





    db.insert(collection="HDAJSKHDKJAS", data=temp_data, _id=hash_id(file_name))

    db.close()

    sys.exit(0)    
    app.run(host='0.0.0.0', port=5000, debug=True)