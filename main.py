# Some built-int modules
# import json
# import os
# import sys
# import pprint
# import datetime
# import random

# Custom modules
# from _Database  import MongoDatabase, DB_Config
# from _TableData import TableData
# from _ExcelVisitor import ExcelVisitor
# from _JsonVisitor  import JSON
# from _Redis import RedisCache
from _Database_Utils import Database_Utils
# from _Hash_Utils import hash_id
from routes import app

# Imported libraries
# from pymongo.periodic_executor import _on_executor_deleted
# from werkzeug   import utils
# from json2html  import json2html
from flask      import Flask, config, render_template, flash, make_response, send_from_directory, redirect, url_for, session, request

def mock_assignAuthorization():
    # Stuff about account login 
    user_rows = {
        '733101' : {'password': '733101', 'rows':[733101]},
        '733121' : {'password': '733121', 'rows':[733121]},
        '733131' : {'password': '733131', 'rows':[733131]},
        '733141' : {'password': '733141', 'rows':[733141]},
        '733151' : {'password': '733151', 'rows':[733151]},
        '填报用户' : {'password' : 'tianbaoyonghu',  'rows':[733101]},
        '上传模板' : {'password' : 'shangchuanmoban','rows':[733101,733121,733131,733141,733151,733165,733177,733189,733201,733213,733225]},
        # 'admin'   : {'password' : 'admin',          'rows':[733101,733121,733131,733141,733151,733165,733177,733189,733201,733213,733225]},
    }
    Database_Utils.add_authorization(user_rows=user_rows)
    return

# =============================================
# main

def main():
    mock_assignAuthorization()
    app.run(host='0.0.0.0', port=5000, debug=True)
    return

if __name__ == "__main__":
    main()
