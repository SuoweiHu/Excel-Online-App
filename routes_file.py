# Some built-int modules
# import json
# from logging import log
# import logging
import os
# import sys
# import pprint
# import datetime
import random
import pprint
from sys import meta_path

# from modules._Database  import MongoDatabase, DB_Config
from modules._TableData import TableData
from modules._ExcelVisitor import ExcelVisitor
from modules._JsonVisitor  import JSON
# from modules._Redis import RedisCache
from modules._Database_Utils import Database_Utils
from modules._Hash_Utils import hash_id

from routes_table_static  import *
from routes_table_static  import *
from routes_table_setting import *

from debugTimer import *

from app import app
# from pymongo.periodic_executor import _on_executor_deleted
# from werkzeug   import utils
# from json2html  import json2html
from flask      import Flask, config, render_template, flash, make_response, send_from_directory, redirect, url_for, session, request

save_json = False # 读取后是否保存为 JSON 文件
save_xlsx = False # 读取后是否保留临时的 Excel 文件

# 上传文件
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

# 路由将会使用这个函数上传 “模版表格” 文件 
def route_upload_file(f, f_name):
    """
    上传文件路由的帮助函数
    """
    # 检查文件类型是否正确
    if('xlsx' not in f_name):
        return render_template("redirect_fileUploaded.html", message=f"上传文件失败, 错误: 文件名为{f_name} (需要为后缀是xlsx的文件)")

    # 检查文件是否已经存在
    elif(f_name.split('.')[0] in Database_Utils.table.list_tableData_collections()):
        return render_template("redirect_fileUploaded.html", message=f"上传文件失败, 错误: 文件/集合已经存在", table_name = f_name)

    # 如果文件一切正常
    else: 
        # 保存为临时文件, 从文件读取内容, 并保存到数据库
        f.save(f'./src/temp/{f_name}') # 临时保存文件
        if(save_xlsx): f.save(f'./src/excel/{f_name}') 

        # 读取Excel文件 (注意: 使用获取单元格绝对值, 公式将不被保留)
        tb_name = f_name
        if(not (os.path.exists(f'./src/temp/{f_name}'))): return redirect('table/all')
        excelReader = ExcelVisitor(f'./src/temp/{f_name}')
        titles      = excelReader.get_titles()
        info_table  = excelReader.get_infoTable()
        oper_table  = excelReader.get_operTable()

        # 存储表格数据到自定义类TableData
        tb_name = tb_name.split('.')[0]
        while(' ' in tb_name): tb_name = tb_name.replace(' ', '')
        ids_list    = [hash_id(str(random.random())) for i in range(len(info_table))]
        tableData = TableData(json=None, tb_name=tb_name, titles=titles, rows=info_table, operators=oper_table, ids=ids_list)
        tableData = generate_tableMeta(tableData=tableData)                     # 生成并上传表格的元数据 (并处理原表格)
        tableData_Json = tableData.toJson()                                     # 将表格数据转化成数据库可以保存的BSON类型
        
        # 确认表头标题是否包含行号栏目（）
        titles = tableData.titles   # 标题
        if("行号" in titles):
            app.logger.debug("发现“行号”标题，进入选择必填列页面")
            pass
        else: 
            app.logger.debug("未发现”行号“标题，进入选择替代列页面")
            return render_template("table_option_multiChoice_idMissing.html", 
                options    = titles,
                submit_url = url_for('route_upload_file_idMissing'),
                tb_name    = tb_name
                )

        # 读取后删除临时表格xlsx文件
        os.remove(f'./src/temp/{f_name}')

        # 保存数据            
        if(save_json): JSON.save(tableData_Json, JSON.PATH+f"{tb_name}.json")   # 如果想暂时存储为JSON文件预览
        Database_Utils.table.upload_table(tb_name.split('.')[0],tableData_Json) # 上传表格到数据库为其表格名为名称的集合

        # 重新定向到 “上传成功页面  ”
        # return redirect(url_for('upload_successRedirect', tb_name=tb_name))
        return render_template('redirect_fileUploaded.html', 
        table_name=tb_name,
        message=f"文件 {f_name} 成功上传")

        # 重新定向到选择 “必填” “预设可改” 的页面
        return redirect(url_for('select_RequredAttribute', tb_name=tb_name, return_aftFinish='False'))

@app.route('/file/select_IdReplAttribute',methods=['GET'])
def route_upload_file_idMissing():
    tb_name = request.args.get("tb_name")
    repl_attribute = request.args.get("choice")
    # 以下内容与route_upload_file中的上传大致类似
    excelReader = ExcelVisitor(f'./src/temp/{tb_name}.xlsx')
    titles      = excelReader.get_titles()
    info_table  = excelReader.get_infoTable()
    oper_table  = excelReader.get_operTable()
    tb_name = tb_name.split('.')[0]
    while(' ' in tb_name): tb_name = tb_name.replace(' ', '')
    ids_list    = [hash_id(str(random.random())) for i in range(len(info_table))]
    tableData = TableData(json=None, tb_name=tb_name, titles=titles, rows=info_table, operators=oper_table, ids=ids_list)
    tableData.titles[tableData.titles.index(repl_attribute)] = "行号"        # 替换行号相关内容
    tableData = generate_tableMeta(tableData=tableData)                   
    tableData_Json = tableData.toJson()   
    os.remove(f'./src/temp/{tb_name}.xlsx')

    if(save_json): JSON.save(tableData_Json, JSON.PATH+f"{tb_name}.json")   
    Database_Utils.table.upload_table(tb_name.split('.')[0],tableData_Json) 
    return redirect(url_for('select_RequredAttribute', tb_name=tb_name, return_aftFinish='False'))

# 上传文件时将会通过这个函数为表格建立元数据表并上传 (也会处理其中的配置列)
def generate_tableMeta(tableData):
    """
    上传文件时将会通过这个函数为表格建立元数据表并上传
    Parameter:
        tableData : TableData 类的数据 
        (注意其中的带 "\{", "\}" 字符的单元格将被识别成需要配置成预设值的单元格)
    """

    # -----配置列-------------------------------------------------
    option_titles     = []
    option_optionDict = {}
    
    """
    key = prefix + identifier + suffix 
    e.g   prefix = "#"
          suffix = "#"
          identifier = "OAO"
          key    = "#OAO#"
    """
    identifier = "@" 
    prefix     = "#"
    suffix     = "#"
    key        = prefix+identifier+suffix

    for i in range(len(tableData.titles)):
        if(tableData.rows[0][i] is not None):
            if(key in tableData.rows[0][i]): 
                option_titles.append(tableData.titles[i])
                option_optionDict[tableData.titles[i]] = (tableData.rows[0][i])[len(key):].split(';')
                tableData.clear_column(tableData.titles[i])
            else: pass
        else: pass

     # -----预设列-------------------------------------------------

    # 老方法 ...
        # ~~ # 查找全部赋值完毕的列 (为以后不能更改的单元格作准备) ~~
        # fixed_titles = []
        # for i in range(len(tableData.titles)):
        #     title = tableData.titles[i]
        #     temp_rows  = [row[i] for row in tableData.rows]
        #     if(None not in temp_rows): fixed_titles.append(title)

    # 新方法
    # 查找有值的列 (为以后没有例外不能更改的预设列)
    fixed_titles  = []
    for i in range(len(tableData.titles)):
        title = tableData.titles[i]
        exist_notNone = False
        j = 0 
        while(j < len(tableData.rows) and (not exist_notNone)):
            item = tableData.rows[j][i] 
            if(item is not None): 
                exist_notNone = True 
            j+=1
        if(exist_notNone): fixed_titles.append(title)

    for title in fixed_titles:
        if(title in option_titles):
            fixed_titles.remove(title)
            


    # ---上传表格的元数据--------------------------------------------
    op_name = session['operator_name']
    op_time = gen_dateTime_str()
    meta = {
        "tb_name"           : tableData.tb_name,
        "count"             : len(tableData.operators),
        "titles"            : tableData.titles,
        "fixed_titles"      : fixed_titles,
        "mustFill_titles"   : [],
        "option_titles"     : option_titles,
        "option_optionDict" : option_optionDict,
        "upload_operator"   : op_name,
        "upload_time"       : op_time,
        "due"               : "",
        "comment"           : ""
    }
    timer = debugTimer(f"上传文件页面 - 开始上传表格元数据", f"完成上传元数据操作 ({tableData.tb_name})")
    timer.start()
    Database_Utils.meta.del_tablemMeta(tb_name=tableData.tb_name)
    Database_Utils.meta.save_tablemMeta(tb_name=tableData.tb_name, meta=meta)
    Database_Utils.meta.load_tablemMeta(tb_name=meta['tb_name'])
    timer.stop()

    return tableData

# 上传成功跳转
@app.route('/upload_success/<string:tb_name>')
def upload_successRedirect(tb_name):
    return render_template("redirect_fileUploaded.html", message=f"成功上传表单, 文件名: {tb_name}", table_name = tb_name)

# 更新成功跳转
@app.route('/update_success/<string:tb_name>')
def update_successRedirect(tb_name):
    return render_template("redirect_fileUploaded.html", message=f"成功更改表单必须填项, 文件名: {tb_name}", table_name = tb_name)


