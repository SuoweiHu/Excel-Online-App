# Some built-int modules
# import json
# from logging import log
# import logging
import os
# import sys
# import pprint
# import datetime
import random

# from modules._Database  import MongoDatabase, DB_Config
from modules._TableData import TableData
from modules._ExcelVisitor import ExcelVisitor
from modules._JsonVisitor  import JSON
# from modules._Redis import RedisCache
from modules._Database_Utils import Database_Utils
from modules._Hash_Utils import hash_id
from routes_table import *


# from pymongo.periodic_executor import _on_executor_deleted
# from werkzeug   import utils
# from app import app
# from json2html  import json2html
from flask      import Flask, config, render_template, flash, make_response, send_from_directory, redirect, url_for, session, request

save_json = False # 读取后是否保存为 JSON 文件
save_xlsx = False # 读取后是否保留临时的 Excel 文件

def route_upload_file(f, f_name):
    """
    上传文件路由的帮助函数
    """
    if('xlsx' not in f_name):
        # 检查文件类型是否正确
        return render_template("redirect_fileUploaded.html", message=f"上传文件失败, 错误: 文件名为{f_name} (需要为后缀是xlsx的文件)")

    elif(f_name.split('.')[0] in Database_Utils.list_tableData_colNames()):
        # 检查文件是否已经存在
        return render_template("redirect_fileUploaded.html", message=f"上传文件失败, 错误: 文件/集合已经存在", table_name = f_name)

    else: 
        # 保存文件, 从文件读取内容, 并保存到数据库
        f.save(f'./src/temp/{f_name}') # 临时保存文件
        if(save_xlsx): f.save(f'./src/excel/{f_name}') 

        # 读取Excel文件 (注意: 公式将不被保留)
        tb_name = f_name
        excelReader = ExcelVisitor(f'./src/temp/{f_name}')
        titles      = excelReader.get_titles()
        info_table  = excelReader.get_infoTable()
        oper_table  = excelReader.get_operTable()
        os.remove(f'./src/temp/{f_name}')# 读取后删除文件
        ids_list    = [hash_id(str(random.random())) for i in range(len(info_table))]

        # 存储表格数据到自定义类TableData
        tableData = TableData(json=None, tb_name=tb_name, titles=titles, rows=info_table, operators=oper_table, ids=ids_list)
        tableData_Json = tableData.toJson()
        if(save_json): JSON.save(tableData_Json, JSON.PATH+f"{tb_name}.json") # 如果想暂时存储为JSON文件预览
        Database_Utils.upload_table(tb_name.split('.')[0],tableData_Json)

        # 查找全部赋值完毕的列 (为以后不能更改的单元格作准备)
        fixed_titles = []
        for i in range(len(tableData.titles)):
            title = tableData.titles[i]
            temp_rows  = [row[i] for row in tableData.rows]
            if(None not in temp_rows): fixed_titles.append(title)

        # 上传表格的元数据
        meta = {
            "tb_name" : tableData.tb_name,
            "count"   : len(tableData.operators),
            "titles"            : tableData.titles,
            "fixed_titles"      : fixed_titles,
            "mustFill_titles"   : [] # TODO: 必须填写栏 ???????
        }
        Database_Utils.meta.save_tablemMeta(tb_name=tableData.tb_name, meta=meta)
        return render_template("redirect_fileUploaded.html", message=f"成功上传文件, 文件名: {f_name}", table_name = f_name)
