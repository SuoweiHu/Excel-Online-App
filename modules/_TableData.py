from os import replace
from pprint import pprint
from json2html import *
from werkzeug.utils import html
import datetime
from ._Hash_Utils import hash_id
import random
import pprint


class TableData:
    operator_titles = ["操作员","时间"]

    tb_name   = None    # 行文档的 _ID (自动生成, 不是行号 !!!!)
    titles    = None    # 表格名称      
    ids       = []      # 表格列标题
    rows      = []      # 表格行数据
    # operators = []      # 预设内容(列标题)
    fixed_titles = []   # 操作员

    # ==============================
    # Store/ Restore from json format (For database)

    # def DEPRECATED__init__(self, tb_name=None, titles=None, rows=None, operators=None, json=None):
        #     """
        #     tb_name :   the file name here should be transferred into hashed prior to 
        #                 loggining into the database
        #     titles:     the titles of the table, should match with the max size of strings 
        #                 within a single row
        #     rows:       existing data of data rows, expecting a 2 dimentioanl array here, 
        #                 alike [[1,None,3], [None,3,4], [4,5,6]]. Where each sublist corresponds 
        #                 a row, and the sequence of data matches with the sequence of titles
        #     """
        #     if(json is None):
        #         self.tb_name    = tb_name   
        #         self.titles     = titles   
        #         self.rows       = rows
        #         if(operators is not None): 
        #             temp_operator = []
        #             for operator in operators:
        #                 if(not len(operator) == 2): operator = [None, None]
        #                 temp_operator.append(operator)
        #             self.operators  = temp_operator
        #         else: 
        #             self.operators  = [{"name":None, "time":None} for _ in range(len(rows))]

        #         # 检查每行的数据数量和表头属性数量相同
        #         for row in rows:
        #             if not (len(row)==len(titles)): 
        #                 raise(f"""
        #                     Number of row entries does not macth with the number of titles.\n 
        #                     (Notice that row can include None, e.g. [1,2,None,3,\'小明\'])  \n
        #                     Title: ({len(titles)})\n\t {titles}
        #                     Row: ({len(row)})\n\t {row}
        #                     """)
        #     else:
        #         # print(json)
        #         self.tb_name   = json["name"]
        #         self.titles    = json["titles"]
        #         self.rows      = json["data"]["rows"]
        #         self.operators = json["data"]["operator"]

        #     return
    # def DEPRECATED__init__(self, tb_name=None, titles=None, rows=None, operators=None, json=None):
        # """
        # tb_name :   the file name here should be transferred into hashed prior to 
        #             loggining into the database
        # titles:     the titles of the table, should match with the max size of strings 
        #             within a single row
        # rows:       existing data of data rows, expecting a 2 dimentioanl array here, 
        #             alike [[1,None,3], [None,3,4], [4,5,6]]. Where each sublist corresponds 
        #             a row, and the sequence of data matches with the sequence of titles

        # input json file datastructure:
        #     {
        #         "name" : "2020第一季度.xlxs",
        #         "data" : [
        #             {"行号" : 123123, “金额” : 111111, "名字" : 22222, "操作员": "胡所未", “操作时间”:“2020-02-02”}
        #             {"行号" : 123123, “金额” : 111111, "名字" : 22222, "操作员": "胡所未", “操作时间”:“2020-02-02”}
        #             {"行号" : 123123, “金额” : 111111, "名字" : 22222, "操作员": "胡所未", “操作时间”:“2020-02-02”}
        #             {"行号" : 123123, “金额” : 111111, "名字" : 22222, "操作员": "胡所未", “操作时间”:“2020-02-02”}
        #         ]
        #     }
        # """
        # if(json is None):
        #     self.tb_name    = tb_name   
        #     self.titles     = titles   
        #     self.rows       = rows
        #     if(operators is not None): 
        #         temp_operator = []
        #         for operator in operators:
        #             if(not len(operator) == 2): operator = [None, None]
        #             temp_operator.append(operator)
        #         self.operators  = temp_operator
        #     else: 
        #         self.operators  = [{"name":None, "time":None} for _ in range(len(rows))]

        #     # 检查每行的数据数量和表头属性数量相同
        #     for row in rows:
        #         if not (len(row)==len(titles)): 
        #             raise(f"""
        #                 Number of row entries does not macth with the number of titles.\n 
        #                 (Notice that row can include None, e.g. [1,2,None,3,\'小明\'])  \n
        #                 Title: ({len(titles)})\n\t {titles}
        #                 Row: ({len(row)})\n\t {row}
        #                 """)
        # else:
        #     # print(json)

        #     # Extract table name
        #     self.tb_name   = json["name"]
        #     table_data = json["data"]

        #     # Extract titles
        #     titles = []
        #     first_row = table_data[0]
        #     for x in first_row.items():
        #         titles.append(x[0])
        #     titles = titles[:-2]    # remove operator columns * 2
        #     self.titles    = titles

        #     # Extract data
        #     table_rows = []
        #     table_operators = []
        #     for row in table_data:
        #         temp_row  = []
        #         temp_oper = []
        #         for i in range(len(titles)):
        #             cell_title = titles[i] 
        #             cell_data = row[cell_title]
        #             temp_row.append(cell_data)
        #         temp_oper.append(row['操作员'])
        #         temp_oper.append(row['操作时间'])

        #         table_rows.append(temp_row)
        #         table_operators.append(temp_oper)
                
        #     self.rows      = table_rows
        #     self.operators = table_operators

        # return
    def __init__(self, json, tb_name, titles=None, rows=None, operators=None, ids=None):
        """
        tb_name :   the file name here should be transferred into hashed prior to 
                    loggining into the database
        titles:     the titles of the table, should match with the max size of strings 
                    within a single row
        rows:       existing data of data rows, expecting a 2 dimentioanl array here, 
                    alike [[1,None,3], [None,3,4], [4,5,6]]. Where each sublist corresponds 
                    a row, and the sequence of data matches with the sequence of titles

        input json file datastructure:
            {
                "name" : "2020第一季度.xlxs",
                "data" : [
                    {"行号" : 123123, “金额” : 111111, "名字" : 22222, "操作员": "胡所未", “操作时间”:“2020-02-02”}
                    {"行号" : 123123, “金额” : 111111, "名字" : 22222, "操作员": "胡所未", “操作时间”:“2020-02-02”}
                    {"行号" : 123123, “金额” : 111111, "名字" : 22222, "操作员": "胡所未", “操作时间”:“2020-02-02”}
                    {"行号" : 123123, “金额” : 111111, "名字" : 22222, "操作员": "胡所未", “操作时间”:“2020-02-02”}
                ]
            }
        """
        # ============================================
        # 如果 Json 字典为 None 那么一般入参是从文件读取中来 (初次读取)
        if(json is None):
            self.ids        = ids       # 行文档的 _ID (自动生成, 不是行号 !!!!)
            self.tb_name    = tb_name   # 表格名称
            self.titles     = titles    # 表格列标题
            self.rows       = rows      # 表格行数据
            # self.fixed_titles = []      # 预设内容(列标题)
            if(operators is not None):  # 操作员
                temp_operator = []
                for operator in operators:
                    if(not len(operator) == 2): operator = [None, None]
                    temp_operator.append(operator)
                self.operators  = temp_operator
            else: 
                self.operators  = [{"name":None, "time":None} for _ in range(len(rows))]

            # 检查每行的数据数量和表头属性数量相同 (若否抛出错误)
            for row in rows:
                if not (len(row)==len(titles)): 
                    raise(f"""
                        Number of row entries does not macth with the number of titles.\n 
                        (Notice that row can include None, e.g. [1,2,None,3,\'小明\'])  \n
                        Title: ({len(titles)})\n\t {titles}
                        Row: ({len(row)})\n\t {row}""")
            
        
        # ============================================
        # 如果 Json 字典不为 None 一般就是从数据库的读取
        else:
            self.tb_name   = tb_name # 表名
            self.titles    = []      # 表属性
            self.ids       = []      # 表行号(_id)
            self.rows      = []      # 表数据
            self.operators = []      # 表操作员
            rows           = list(json.items()) # 表

            # 读取标题 ===============
            first_row_data = rows[0][1]['data']
            for item in first_row_data.items():
                self.titles.append(item[0])

            # 读取ID ================
            for row in rows:
                _id = row[0]
                self.ids.append(_id)

            # 内容, 操作员 ===========
            for row in rows:
                row = row[1] 
                # 内容 ==============
                data = row['data']
                r_data = []
                for i in range(len(self.titles)):
                    title  = self.titles[i]
                    t_data = data[title]
                    r_data.append(t_data)
                self.rows.append(r_data)
                # 操作员 ============
                if('user' in row.keys()):
                    user = row['user']
                    self.operators.append([user['name'], user['time']])
                else:
                    self.operators.append([None, None])

        return

    # def DEPRECATED_toJson(self):
        # """
        # 将该类转化为字段, 为入库/存储为JSON文件作准备, 转化后的数据类似如下
        # transformed_dict = {
        #     "name": "2020年二季度"
        #     "titles" : ["行号","项目号","子账户","账户名","分账户","账户名","受理人","金额"],
        #     "data"   : {
        #         "rows" :    [
        #                         ["733101","213123","A","XXXX","A1","XXXX","小S",None],
        #                         ["733121","123123","A","XXXX","A1","XXXX","小B","321"],
        #                         ["733131","123123","B","YYYY","B1","YYYY 1",None,"123"],
        #                         ["733141","123123","B","YYYY",None,None,None,"123"],
        #                         ["733151","1231231","B","YYYY","B3","YYYY 3","小B",None]
        #                     ],
        #         "operator" :[
        #                         {"name":"张三", "time":"2020.02.11 - 11:00:21"},
        #                         {"name":"李四", "time":"2020.02.11 - 11:00:21"},
        #                         {"name":"李四", "time":"2020.02.11 - 11:00:21"},
        #                         {"name":"王五", "time":"2020.02.11 - 11:00:21"},
        #                         {"name":"张三", "time":"2020.02.11 - 11:00:21"},
        #                     ]
        #     }
        # }
        # """
        # table_dict = {}
        # table_dict["name"]             = self.tb_name
        # table_dict["titles"]           = self.titles
        # table_dict["data"]             = {"rows":[], "operator":[]}
        # table_dict["data"]["rows"]     = self.rows
        # table_dict["data"]["operator"] = self.operators
        # return table_dict   
    # def DEPRECATED_toJson(self):
        # """
        # 将该类转化为字段, 为入库/存储为JSON文件作准备, 转化后的数据类似如下
        # {
        #     "name" : "2020第一季度.xlxs",
        #     "data" : [
        #         {"行号" : 123123, “金额” : 111111, "名字" : 22222, "操作员": "胡所未", “操作时间”:“2020-02-02”}
        #         {"行号" : 123124, “金额” : 111111, "名字" : 22222, "操作员": "胡所未", “操作时间”:“2020-02-02”}
        #         {"行号" : 123123, “金额” : 111111, "名字" : 22222, "操作员": "胡所未", “操作时间”:“2020-02-02”}
        #         {"行号" : 123123, “金额” : 111111, "名字" : 22222, "操作员": "胡所未", “操作时间”:“2020-02-02”}
        #     ]
        # }
        # """
        # table_dict = {}
        # table_dict["name"] = self.tb_name
        # table_dict["data"] = []
        # for i in range(len(self.rows)):
        #     row_dict = {}
        #     operator = self.operators[i]
        #     data_row = self.rows[i]
        #     for j in range(len(self.titles)):  # insert row normal data (除了操作员意外的数据)
        #         cell_title = self.titles[j]
        #         cell_data = data_row[j]
        #         row_dict[cell_title] = cell_data
        #     row_dict["操作员"] = operator[0]
        #     row_dict["操作时间"] = operator[1]  # insert operator data
        #     table_dict["data"].append(row_dict)

        # return table_dict   
    # def DEPRECATED_toJson(self, key="行号"):
        # """
        # 将该类转化为字段, 为入库/存储为JSON文件作准备, 转化后的数据类似如下
        # {
        #     "name" : "2020第一季度.xlxs",
        #     "data" : {
        #         123123: {"行号" : 123123, “金额” : 111111, "名字" : 22222, "操作员": "胡所未", “操作时间”:“2020-02-02”}
        #         123124: {"行号" : 123124, “金额” : 111111, "名字" : 22222, "操作员": "胡所未", “操作时间”:“2020-02-02”}
        #         123125: {"行号" : 123125, “金额” : 111111, "名字" : 22222, "操作员": "胡所未", “操作时间”:“2020-02-02”}
        #         123126: {"行号" : 123126, “金额” : 111111, "名字" : 22222, "操作员": "胡所未", “操作时间”:“2020-02-02”}
        #     }
        # }
        # """
        # table_dict = {}
        # table_dict["name"] = self.tb_name
        # table_dict["data"] = {}
        # for i in range(len(self.rows)):
        #     row_dict = {}
        #     operator = self.operators[i]
        #     data_row = self.rows[i]
        #     for j in range(len(self.titles)):  # insert row normal data (除了操作员意外的数据)
        #         cell_title = self.titles[j]
        #         cell_data = data_row[j]
        #         row_dict[cell_title] = cell_data
        #     row_dict["操作员"] = operator[0]
        #     row_dict["操作时间"] = operator[1]  # insert operator data
        #     table_dict["data"][row_dict[key]] = row_dict

        # return table_dict   
    
    def toJson(self):
        """
        将该类转化为字段, 为入库/存储为JSON文件作准备, 转化后的数据类似如下
        {
            89dsad29jkdashkj8udasiud: { data:{"行号" : 123123, “金额” : 111111, "名字" : 22222},    user:{"操作员": "SomeOne", “操作时间”:“2020-02-02”}}
            kdashkjad8kdashkad29jkj8: { data:{"行号" : 123124, “金额” : 111111, "名字" : 22222},    user:{"操作员": "SomeOne", “操作时间”:“2020-02-02”}}
            1231kdashkjad8kdashjkj83: { data:{"行号" : 123125, “金额” : 111111, "名字" : 22222},    user:{"操作员": "SomeOne", “操作时间”:“2020-02-02”}}
            4kldsakdashkjad8kj82e21d: { data:{"行号" : 123126, “金额” : 111111, "名字" : 22222},    user:{"操作员": "SomeOne", “操作时间”:“2020-02-02”}}
        }
        """
        rtn_dict = {}
        for i in range(len(self.rows)):
            # 取出每行的ID
            row_id = self.ids[i]

            # 导入每行的数据(非操作员数据)
            data_dict = {}
            data_row = self.rows[i]
            for j in range(len(self.titles)):  
                cell_title = self.titles[j]
                cell_data = data_row[j]
                data_dict[cell_title] = cell_data

            # 导入每行的操作员信息
            user_dict = {}
            operator = self.operators[i]
            user_dict["name"] = operator[0]
            user_dict["time"] = operator[1] 

            rtn_dict[row_id] = {'data':data_dict, 'user':user_dict}

        return rtn_dict   
    
    # ==============================
    # Transform to html form (For flask application)
    def tableShow_toJson(self, rows_of_keys, key="行号", show_operator=False):
        tb_name     = self.tb_name
        tb_name     = tb_name.replace(".xlsx", "") 
        titles      = self.titles
        rows        = self.rows
        operators   = self.operators
        key = self.titles.index(key) 

        # -----------------------------------------------
        # 如果rows_of_keys没有入参, 那就默认是管理员, 展示所有表格
        if(rows_of_keys is None):
            rows_of_keys = []
            for row in self.rows:
                rows_of_keys.append(row[key])

        # 转一下格式
        temp_list=[]
        for row_key in rows_of_keys: temp_list.append(str(row_key))
        rows_of_keys = temp_list

        # -----------------------------------------------
        # 根据权限, 仅加入允许展示的行 (key in rows_of_keys)
        rtn_list = []
        for i in range(len(rows)):
            cur_row = rows[i]

            # -------------------
            # 如果有权限读取...
            if(cur_row[key] in rows_of_keys): 
                cur_operator = operators[i]
                temp_dict = {}

                # Information columns' placehpolder
                for j in range(len(titles)):
                    temp_dict[titles[j]] = ""

                # Operator
                if(show_operator):
                    # temp_dict[" "]       = " "    # Spacing
                    temp_dict["操作员"]   = cur_operator[0]
                    temp_dict["时间"]     = cur_operator[1]
                    if(temp_dict["操作员"] is None): temp_dict["操作员"]   = ""
                    if(temp_dict["时间"]   is None): temp_dict["时间"]    = ""

                # Information columns
                for j in range(len(titles)):
                    # temp_dict[titles[j]] = cur_row[j]
                    temp_val = cur_row[j]
                    # 处理数据可能缺省的部分
                    if(temp_val is None):
                        temp_dict[titles[j]] = ""
                    else: 
                        temp_dict[titles[j]] = temp_val

                # 添加可替代值
                if(cur_operator[0] is None) and (cur_operator[1] is None):
                    temp_dict["操作"] = f"@@@@[{self.ids[i]}]####"
                else:
                    temp_dict["操作"] = f"@@@@@@@@[{self.ids[i]}]########"

                # Append to existing list
                rtn_list.append(temp_dict)
            # -------------------
        # -----------------------------------------------
        return rtn_list
        rtn_dict = {tb_name:rtn_list}
        return rtn_dict
    def tableShow_toHtml(self, rows_of_keys, show_operator = True):
        json_dict = self.tableShow_toJson(rows_of_keys=rows_of_keys,show_operator=show_operator)
        html_string = json2html.convert(json = json_dict)

        # ================================================================================
        # html_string = html_string.replace("""<table border="1">""", """<table class="layui-table" lay-data="{height:315, page:true}" lay-filter="test">""")
        # html_string = html_string.replace("""<table border="1">""", """ <table class="layui-table"   lay-data="{height:315, page:true}"> """)
        html_string = html_string.replace("""<table border="1">""", """ <table lay-filter="table_show"> """)
        # ================================================================================
        x = html_string.count("""<th>""")
        prev_position = 0
        for i in range(x):
            from_ = html_string.find("<th>", prev_position)
            to_   = html_string.find("</th>",from_)
            prev_position = to_
            title = html_string[from_+4: to_]
            # html_string = html_string.replace("""<th>""", """<th lay-data="{field:'"""+str(random.random())+"""', width:auto}">""", 1)
            # html_string = html_string.replace("""<th>""", """<th lay-data="{field:'"""+str(random.random())+"""', sort:true}">""", 1)
            if((x-i)==x):  html_string = html_string.replace("""<th>""", """<th lay-data="{field:'"""  +str(title)+  """\', unresize:true, width:80, fixed: \'left\',  align:'center'}">""", 1)
            elif((x-i)==1):html_string = html_string.replace("""<th>""", """<th lay-data="{field:'"""  +str(title)+  """\', unresize:true, width:95, fixed: \'right\', align:'center'}">""", 1)
            else:          html_string = html_string.replace("""<th>""", """<th lay-data="{field:'"""  +str(title)+  """\', align:'center', unresize:false}">""", 1)
        # ================================================================================

        replace_dict = {
            # "@@@@@@@@["   : f"""<form action="/table/edit" method="get"><input type="hidden" name="table_name" value='{self.tb_name}'><input type="hidden" name="row_id" value='""",
            "@@@@@@@@["     : f"""<form action="/table/edit" method="get"><input type="hidden" name="table_name" value='{self.tb_name}'><input type="hidden" name="row_id" value='""",
            "@@@@["         : f"""<form action="/table/edit" method="get"><input type="hidden" name="table_name" value='{self.tb_name}'><input type="hidden" name="row_id" value='""",
            # "]########"   : f"""'><input class="layui-btn layui-btn-disabled layui-btn-sm" style="margin-left:0%;" type="submit" disabled value="已经编辑"></form>""",
            "]########"     : f"""'><input class="layui-btn layui-btn-xs layui-btn-primary"  style="margin-left:0%;" type="submit" value="已经编辑"></form>""",
            "]####"         : f"""'><input class="layui-btn layui-btn-xs"  style="margin-left:0%;" type="submit" value="编辑此行"></form>""",
         }
        for replace_tuple in replace_dict.items():html_string = html_string.replace(replace_tuple[0], replace_tuple[1])
        return html_string

    # def DEPRECATEd_tableEdit_toJson(self, show_operator=True, replace_noneWithInput=True):
        # """
        # 将该类转化为字段, 为入库/存储为JSON文件作准备, 转化后的数据类似如下
        # transformed_dict = {
        #     "2020年二季度":[
        #         {"行号":"733101","项目号":"213123","子账户":"A","账户名":"XXXX","分账户":"A1","账户名":"YYY","受理人":"小S","金额":"123"},
        #         {"行号":"733101","项目号":"213123","子账户":"A","账户名":"XXXX","分账户":"A1","账户名":"YYY","受理人":"小S","金额":"123"},
        #         {"行号":"733101","项目号":"213123","子账户":"A","账户名":"XXXX","分账户":"A1","账户名":"YYY","受理人":"小S","金额":"123"},
        #         {"行号":"733101","项目号":"213123","子账户":"A","账户名":"XXXX","分账户":"A1","账户名":"YYY","受理人":"小S","金额":"123"},
        #     ]
        # }
        # """
        # tb_name     = self.tb_name
        # tb_name     = tb_name.replace(".xlsx", "") 
        # titles      = self.titles
        # rows        = self.rows
        # operators   = self.operators

        # rtn_list = []

        # for i in range(len(rows)):
        #     cur_row = rows[i]
        #     cur_operator = operators[i]
        #     temp_dict = {}

        #     # Information columns' placehpolder
        #     for j in range(len(titles)):
        #         temp_dict[titles[j]] = ""

        #     # Operator
        #     if(show_operator):
        #         # temp_dict[" "]       = " "    # Spacing
        #         temp_dict["操作员"]   = cur_operator[0]
        #         temp_dict["时间"]     = cur_operator[1]
        #         if(temp_dict["操作员"] is None): temp_dict["操作员"]   = ""
        #         if(temp_dict["时间"]   is None): temp_dict["时间"]    = ""

        #     # Information columns
        #     for j in range(len(titles)):
        #         # temp_dict[titles[j]] = cur_row[j]
        #         temp_val = cur_row[j]
        #         # 处理正常数据部分
        #         if((temp_val is None) and (replace_noneWithInput) and not ((titles[j]=="操作员") or (titles[j]=="时间"))): 
        #             # temp_dict[titles[j]] = (f"""<input type="text" name="{str(i) + "_" + str(titles[j])}">""")
        #             # temp_dict[titles[j]] = (f"""None_{str(i)}_{str(titles[j])}""")
        #             # temp_dict[titles[j]] = (f"""None_{str(i)}_{str(j)}""")
        #             temp_dict[titles[j]] = (f"""###{str(i)}_{str(titles[j])}@@@""")
        #         # 处理操作员部分
        #         elif((temp_val is None) and (replace_noneWithInput) and ((titles[j]=="操作员") or (titles[j]=="时间"))): 
        #             temp_dict[titles[j]] = ""
        #         else: 
        #             temp_dict[titles[j]] = temp_val


        #     # Append to existing list
        #     rtn_list.append(temp_dict)

        # rtn_dict = {tb_name:rtn_list}
        # return rtn_dict
    # def DEPRECATEd_tableEdit_toHtml(self, json_dict=None, show_operator = True, replace_noneWithInput=True):
        # """
        # convert the table data into representational language, for instance
        # <table border="1">
        #     <tr>
        #         <th>2020年二季度.xlsx</th>
        #         <td>
        #             <table border="1">
        #                 <thead>
        #                     <tr>
        #                         <th>行号</th>
        #                         <th>项目号</th>
        #                         <th>子账户</th>
        #                         <th>账户名</th>
        #                         <th>分账户</th>
        #                         <th>受理人</th>
        #                         <th>金额</th>
        #                         <th>操作员</th>
        #                         <th>时间</th>
        #                     </tr>
        #                 </thead>
        #                 <tbody>
        #                     <tr>
        #                         <td>733101</td>
        #                         <td>213123</td>
        #                         <td>A</td>
        #                         <td>None</td>
        #                         <td>None</td>
        #                         <td>None</td>
        #                         <td>None</td>
        #                         <td>None</td>
        #                         <td>None</td>
        #                     </tr>
        #                     <tr>
        #                         <td>733121</td>
        #                         <td>123123</td>
        #                         <td>A</td>
        #                         <td>XXXX</td>
        #                         <td>A1</td>
        #                         <td>小B</td>
        #                         <td>321</td>
        #                         <td>李四</td>
        #                         <td>2020.02.11 - 11:00:22</td>
        #                     </tr>
        #                     <tr>
        #                         <td>733131</td>
        #                         <td>123123</td>
        #                         <td>B</td>
        #                         <td>YYYY 1</td>
        #                         <td>B1</td>
        #                         <td>None</td>
        #                         <td>123</td>
        #                         <td>王五</td>
        #                         <td>2020.02.11 - 11:00:23</td>
        #                     </tr>
        #                     <tr>
        #                         <td>733141</td>
        #                         <td>123123</td>
        #                         <td>B</td>
        #                         <td>None</td>
        #                         <td>None</td>
        #                         <td>None</td>
        #                         <td>123</td>
        #                         <td>None</td>
        #                         <td>None</td>
        #                     </tr>
        #                     <tr>
        #                         <td>733151</td>
        #                         <td>1231231</td>
        #                         <td>B</td>
        #                         <td>YYYY 3</td>
        #                         <td>B3</td>
        #                         <td>小B</td>
        #                         <td>None</td>
        #                         <td>张三</td>
        #                         <td>2020.02.11 - 11:00:25</td>
        #                     </tr>
        #                 </tbody>
        #             </table>
        #         </td>
        #     </tr>
        # </table>
        # """ 
        # # Convert the json dict into human readable table in html
        # if(json_dict is None): 
        #     json_dict = self.tableEdit_toJson(show_operator=show_operator)
        # html_string = json2html.convert(json = json_dict)

        # # Process the table such that none becomes form
        # replace_dict = {
        #     "###" : "<input type=\"text\" name=\"",
        #     "@@@" : "\">",
        #  }
        # if(replace_noneWithInput):
        #     for replace_tuple in replace_dict.items():
        #         html_string = html_string.replace(replace_tuple[0], replace_tuple[1])
        #         # html_string.replace(replace_tuple[0], replace_tuple[1])

        # # Add form info into string 
        # now = datetime.datetime.now()
        # day = now.date()
        # time = now.time()
        # day_str = day.__format__('%y/%m/%d')
        # time_str = time.strftime('%H:%M:%S')
        # datetime_str = f"{day_str} {time_str}"

        # # 添加标题,结尾,提交按钮等信息
        #     # html_string = """
        #     #     <form action="/upload" method="get">
        #     #     <h2>表单数据</h2>""" + \
        #     #     html_string + \
        #     #     """<br><hr>"""

        #     # html_string += f"""
        #     #     <h2>操作员</h2>
        #     #     名字: &nbsp <input type="text" name="operator_name" required> <br>
        #     #     时间: &nbsp <input type="text" name="operator_time" required value="{datetime_str}"> <br>
        #     #     <br>
        #     #     <input type="submit" value="Submit">
        #     #     """
        #     # html_string += """</form>""" 

        # return html_string
    def tableEdit_toJson(self, row_of_key=None, key="行号", show_operator=False):
        tb_name     = self.tb_name
        tb_name     = tb_name.replace(".xlsx", "") 
        titles      = self.titles
        rows        = self.rows
        operators   = self.operators
        key = self.titles.index(key) 
        row_of_key = str(row_of_key)

        # -----------------------------------------------
        # 根据权限, 仅加入允许展示的行 (key in rows_of_keys)
        rtn_list = []
        for i in range(len(rows)):
            # print(self.ids[i])
            # print(row_of_key)
            # -------------------
            # 如果有权限读取...
            if(self.ids[i] == row_of_key): 
                cur_row = rows[i]
                cur_operator = operators[i]
                temp_dict = {}

                # Information columns' placehpolder
                for j in range(len(titles)):
                    temp_dict[titles[j]] = ""

                # Operator
                if(show_operator):
                    # temp_dict[" "]       = " "    # Spacing
                    temp_dict["操作员"]   = cur_operator[0]
                    temp_dict["时间"]     = cur_operator[1]
                    if(temp_dict["操作员"] is None): temp_dict["操作员"]   = ""
                    if(temp_dict["时间"]   is None): temp_dict["时间"]    = ""

                # Information columns
                for j in range(len(titles)):
                    # temp_dict[titles[j]] = cur_row[j]
                    temp_val = cur_row[j]
                    
                    # 处理数据可能缺省的部分
                    if(temp_val is None)   and ((titles[j]=="操作员") or (titles[j]=="时间")):
                        # 如果是操作员行
                        temp_dict[titles[j]] = ""
                    elif(titles[j]=="行号"): 
                        # 如果是索引行
                        temp_dict[titles[j]] = temp_val
                    elif(temp_val is None) and not ((titles[j]=="操作员") or (titles[j]=="时间")):
                        # 如果是普通数据行 - 且未经填写
                        temp_dict[titles[j]] = (f"""@@@@@@@@#@@@@@@@@[{str(titles[j])}]########""")
                    else: 
                        # 如果是普通数据行 - 且已经填写
                        temp_dict[titles[j]] = (f"""@@@@@@@@#{str(temp_val)}@@@@@@@@[{str(titles[j])}]########""")
                        # temp_dict[titles[j]] = temp_val

                # 添加可替代值
                temp_dict["操作"] = f"@@@@{self.ids[i]}####"
                # Append to existing list
                rtn_list.append(temp_dict)
            # -------------------
        # -----------------------------------------------
        return rtn_list
        rtn_dict = {tb_name:rtn_list}
        return rtn_dict
    # def tableEdit_toJson_s(self, row_of_keys=None, key="行号", show_operator=False):
        # tb_name     = self.tb_name
        # tb_name     = tb_name.replace(".xlsx", "") 
        # titles      = self.titles
        # rows        = self.rows
        # operators   = self.operators 

        # # -----------------------------------------------
        # # 根据权限, 仅加入允许展示的行 (key in rows_of_keys)
        # rtn_list = []
        # for row_of_key in row_of_keys:
        #     temp_list = self.tableEdit_toJson(row_of_key=row_of_key, key=key, show_operator=show_operator)
        #     rtn_list = rtn_list + temp_list[tb_name]

      
        # rtn_dict = {tb_name:rtn_list}
        # return rtn_dict
    def tableEdit_toHtml(self, row_of_key=None, show_operator = True):
        json_dict = self.tableEdit_toJson(row_of_key=row_of_key,show_operator=show_operator)
        html_string = json2html.convert(json = json_dict)

        # ================================================================================
        # html_string = html_string.replace("""<table border="1">""", """<table class="layui-table" lay-data="{width:1800}">""")
        html_string = html_string.replace("""<table border="1">""", """<table class="layui-table" """)
        # html_string = html_string.replace("""<table border="1">""", """<table class="layui-table" lay-filter="table_edit">""")

        # html_string = html_string.replace("""<table border="1">""", """ <table lay-filter="table_edit"> """)
        # html_string = html_string.replace("""<table border="1">""", """ <table lay-filter="table_edit"> <form action="/table/submit" method="post">""")
        # html_string = html_string.replace("""</table>""", """ </table> </form>""")
        # ================================================================================
        x = html_string.count("""<th>""")
        prev_position = 0
        for i in range(x):
            from_ = html_string.find("<th>", prev_position)
            to_   = html_string.find("</th>",from_)
            prev_position = to_
            title = html_string[from_+4: to_]
            
            # html_string = html_string.replace("""<th>""", """<th lay-data="{field:'"""+str(random.random())+"""', width:auto}">""", 1)
            # html_string = html_string.replace("""<th>""", """<th lay-data="{field:'"""+str(random.random())+"""', sort:true}">""", 1)
            if((x-i)==x):  html_string = html_string.replace("""<th>""", """<th lay-data="{field:'"""  +str(title)+  """\', unresize:true, width:80, fixed: \'left\',  align:'center'}">""", 1)
            elif((x-i)==1):html_string = html_string.replace("""<th>""", """<th lay-data="{field:'"""  +str(title)+  """\', unresize:true, width:95, fixed: \'right\', align:'center'}">""", 1)
            else:          html_string = html_string.replace("""<th>""", """<th lay-data="{field:'"""  +str(title)+  """\', align:'center', unresize:false, width:250}">""", 1)
        # ================================================================================
        html_string = html_string.replace("""<td>""", """<td style="width:20px">""", 1)


        # # Process the table such that none becomes form
        replace_dict = {
            # "@@@@@@@@#" : """<input type="text" style="height:26px" required value='""", # 若必须填写
            "@@@@@@@@#" : """<input type="text" style="height:26px" value='""",            # 若非必须填写
            "@@@@@@@@[" : """' autocomplete="off" class="layui-input" name='""",
            "]########" : """'> """,
            "@@@@"      : f"""<input type="hidden" name="table_name" value='{self.tb_name}'><input type="hidden" name="row_id" value='""",
            "####"      : """'><input  class="layui-btn layui-btn-xs" type="submit" value="提交更改">"""
         }
        for replace_tuple in replace_dict.items():html_string = html_string.replace(replace_tuple[0], replace_tuple[1])

        html_string = """<form action="/table/submit" method="post">""" + html_string
        html_string = html_string + """</form>"""
        return html_string

    # def tableEdit_toHtml_s(self, row_of_keys=None, show_operator = True):
        # json_dict = self.tableEdit_toJson_s(row_of_keys=row_of_keys,show_operator=show_operator)
        # html_string = json2html.convert(json = json_dict)
        # html_string = html_string.replace("""<table border="1">""", """<table class="layui-table">""")

        # # # Process the table such that none becomes form
        # replace_dict = {
        #     # "@@@@@@@@#" : """<input type="text" required value='""", # 若必须填写
        #     "@@@@@@@@#" : """<input type="text" value='""",            # 若非必须填写
        #     "@@@@@@@@[" : """' autocomplete="off" class="layui-input" name='""",
        #     "]########" : """'> """,
        #     "@@@@"      : f"""<input type="hidden" name="table_name" value='{self.tb_name}'><input type="hidden" name="row_id" value='""",
        #     "####"      : """'><input  class="layui-btn" type="submit" value="提交更改">"""
        #  }
        # for replace_tuple in replace_dict.items():html_string = html_string.replace(replace_tuple[0], replace_tuple[1])

        # html_string = """<form action="/table/submit" method="post">""" + html_string
        # html_string = html_string + """</form>"""
        # return html_string

    # ================================
    def get_row_id(self,bank_nos, key="行号"):
        """
        Get input param of a list of bank numbers and return a list of rows 
        in the table that have {key} equal to the bank number for later access
        """
        rtn = []
        key_index = self.titles.index(key)
        for bank_no in bank_nos:
            for i in range(len(self.rows)):
                if(str(bank_no) == str((self.rows[i])[key_index])):
                    rtn.append(self.ids[i])
        return rtn
