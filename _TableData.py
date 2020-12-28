from os import replace
from json2html import *
from werkzeug.utils import html
import datetime


class TableData:
    """
    Usage:
        tbname = "2020年二季度"
        titles = ["行号","项目号","子账户","账户名","分账户","账户名","受理人","金额"]
        rows   = [["733101","213123","A","XXXX","A1","XXXX","小S",None],
                  ["733121","123123","A","XXXX","A1","XXXX","小B","321"],
                  ["733131","123123","B","YYYY","B1","YYYY 1",None,"123"],
                  ["733141","123123","B","YYYY",None,None,None,"123"],
                  ["733151","1231231","B","YYYY","B3","YYYY 3","小B",None]]
        operators = [[None, None],
                     [小明, 2020.02.11-23:32:10],
                     [小花, 2020.03.12-23:32:10],
                     [小百, 2020.04.13-23:32:10],
                     [None, None]]
        tb_data = TableData(tb_name= tbname, titles=titles, rows=rows, operators=operators)
    """

    tb_name  = None
    titles   = None
    rows     = []
    operators = []

    def __init__(self, tb_name=None, titles=None, rows=None, operators=None, json=None):
        """
        tb_name :   the file name here should be transferred into hashed prior to 
                    loggining into the database
        titles:     the titles of the table, should match with the max size of strings 
                    within a single row
        rows:       existing data of data rows, expecting a 2 dimentioanl array here, 
                    alike [[1,None,3], [None,3,4], [4,5,6]]. Where each sublist corresponds 
                    a row, and the sequence of data matches with the sequence of titles
        """
        if(json is None):
            self.tb_name    = tb_name   
            self.titles     = titles   
            self.rows       = rows
            if(operators is not None): 
                temp_operator = []
                for operator in operators:
                    if(not len(operator) == 2): operator = [None, None]
                    temp_operator.append(operator)
                self.operators  = temp_operator
            else: 
                self.operators  = [{"name":None, "time":None} for _ in range(len(rows))]

            # 检查每行的数据数量和表头属性数量相同
            for row in rows:
                if not (len(row)==len(titles)): 
                    raise(f"""
                        Number of row entries does not macth with the number of titles.\n 
                        (Notice that row can include None, e.g. [1,2,None,3,\'小明\'])  \n
                        Title: ({len(titles)})\n\t {titles}
                        Row: ({len(row)})\n\t {row}
                        """)
        else:
            print(json)
            self.tb_name   = json["name"]
            self.titles    = json["titles"]
            self.rows      = json["data"]["rows"]
            self.operators = json["data"]["operator"]

        return

    def to_dict(self):
        """
        将该类转化为字段, 为入库/存储为JSON文件作准备, 转化后的数据类似如下
        transformed_dict = {
            "name": "2020年二季度"
            "titles" : ["行号","项目号","子账户","账户名","分账户","账户名","受理人","金额"],
            "data"   : {
                "rows" :    [
                                ["733101","213123","A","XXXX","A1","XXXX","小S",None],
                                ["733121","123123","A","XXXX","A1","XXXX","小B","321"],
                                ["733131","123123","B","YYYY","B1","YYYY 1",None,"123"],
                                ["733141","123123","B","YYYY",None,None,None,"123"],
                                ["733151","1231231","B","YYYY","B3","YYYY 3","小B",None]
                            ],
                "operator" :[
                                {"name":"张三", "time":"2020.02.11 - 11:00:21"},
                                {"name":"李四", "time":"2020.02.11 - 11:00:21"},
                                {"name":"李四", "time":"2020.02.11 - 11:00:21"},
                                {"name":"王五", "time":"2020.02.11 - 11:00:21"},
                                {"name":"张三", "time":"2020.02.11 - 11:00:21"},
                            ]
            }
        }
        """
        table_dict = {}
        table_dict["name"]             = self.tb_name
        table_dict["titles"]           = self.titles
        table_dict["data"]             = {"rows":[], "operator":[]}
        table_dict["data"]["rows"]     = self.rows
        table_dict["data"]["operator"] = self.operators
        return table_dict   

    def to_dict_json2html(self, show_operator=True, replace_noneWithInput=True):
        """
        将该类转化为字段, 为入库/存储为JSON文件作准备, 转化后的数据类似如下
        transformed_dict = {
            "2020年二季度":[
                {"行号":"733101","项目号":"213123","子账户":"A","账户名":"XXXX","分账户":"A1","账户名":"YYY","受理人":"小S","金额":"123"},
                {"行号":"733101","项目号":"213123","子账户":"A","账户名":"XXXX","分账户":"A1","账户名":"YYY","受理人":"小S","金额":"123"},
                {"行号":"733101","项目号":"213123","子账户":"A","账户名":"XXXX","分账户":"A1","账户名":"YYY","受理人":"小S","金额":"123"},
                {"行号":"733101","项目号":"213123","子账户":"A","账户名":"XXXX","分账户":"A1","账户名":"YYY","受理人":"小S","金额":"123"},
            ]
        }
        """
        tb_name     = self.tb_name
        titles      = self.titles
        rows        = self.rows
        operators   = self.operators

        rtn_list = []

        for i in range(len(rows)):
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
                # 处理正常数据部分
                if((temp_val is None) and (replace_noneWithInput) and not ((titles[j]=="操作员") or (titles[j]=="时间"))): 
                    # temp_dict[titles[j]] = (f"""<input type="text" name="{str(i) + "_" + str(titles[j])}">""")
                    # temp_dict[titles[j]] = (f"""None_{str(i)}_{str(titles[j])}""")
                    # temp_dict[titles[j]] = (f"""None_{str(i)}_{str(j)}""")
                    temp_dict[titles[j]] = (f"""###{str(i)}_{str(titles[j])}@@@""")
                # 处理操作员部分
                elif((temp_val is None) and (replace_noneWithInput) and ((titles[j]=="操作员") or (titles[j]=="时间"))): 
                    temp_dict[titles[j]] = ""
                else: 
                    temp_dict[titles[j]] = temp_val


            # Append to existing list
            rtn_list.append(temp_dict)

        rtn_dict = {tb_name:rtn_list}
        return rtn_dict

    def to_html(self, json_dict=None, show_operator = True, replace_noneWithInput=True):
        """
        convert the table data into representational language, for instance
        <table border="1">
            <tr>
                <th>2020年二季度.xlsx</th>
                <td>
                    <table border="1">
                        <thead>
                            <tr>
                                <th>行号</th>
                                <th>项目号</th>
                                <th>子账户</th>
                                <th>账户名</th>
                                <th>分账户</th>
                                <th>受理人</th>
                                <th>金额</th>
                                <th>操作员</th>
                                <th>时间</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>733101</td>
                                <td>213123</td>
                                <td>A</td>
                                <td>None</td>
                                <td>None</td>
                                <td>None</td>
                                <td>None</td>
                                <td>None</td>
                                <td>None</td>
                            </tr>
                            <tr>
                                <td>733121</td>
                                <td>123123</td>
                                <td>A</td>
                                <td>XXXX</td>
                                <td>A1</td>
                                <td>小B</td>
                                <td>321</td>
                                <td>李四</td>
                                <td>2020.02.11 - 11:00:22</td>
                            </tr>
                            <tr>
                                <td>733131</td>
                                <td>123123</td>
                                <td>B</td>
                                <td>YYYY 1</td>
                                <td>B1</td>
                                <td>None</td>
                                <td>123</td>
                                <td>王五</td>
                                <td>2020.02.11 - 11:00:23</td>
                            </tr>
                            <tr>
                                <td>733141</td>
                                <td>123123</td>
                                <td>B</td>
                                <td>None</td>
                                <td>None</td>
                                <td>None</td>
                                <td>123</td>
                                <td>None</td>
                                <td>None</td>
                            </tr>
                            <tr>
                                <td>733151</td>
                                <td>1231231</td>
                                <td>B</td>
                                <td>YYYY 3</td>
                                <td>B3</td>
                                <td>小B</td>
                                <td>None</td>
                                <td>张三</td>
                                <td>2020.02.11 - 11:00:25</td>
                            </tr>
                        </tbody>
                    </table>
                </td>
            </tr>
        </table>
        """ 
        # Convert the json dict into human readable table in html
        if(json_dict is None): 
            json_dict = self.to_dict_json2html(show_operator=show_operator)
        html_string = json2html.convert(json = json_dict)

        # Process the table such that none becomes form
        replace_dict = {
            "###" : "<input type=\"text\" name=\"",
            "@@@" : "\">",
         }
        if(replace_noneWithInput):
            for replace_tuple in replace_dict.items():
                html_string = html_string.replace(replace_tuple[0], replace_tuple[1])
                # html_string.replace(replace_tuple[0], replace_tuple[1])

        # Add form info into string 
        now = datetime.datetime.now()
        day = now.date()
        time = now.time()
        day_str = day.__format__('%y/%m/%d')
        time_str = time.strftime('%H:%M:%S')
        datetime_str = f"{day_str} {time_str}"

        html_string = """
            <form action="/upload" method="get">
            <h2>表单数据</h2>""" + \
            html_string + \
            """<br><hr>"""

        html_string += f"""
            <h2>操作员</h2>
            名字: &nbsp <input type="text" name="operator_name" required> <br>
            时间: &nbsp <input type="text" name="operator_time" required value="{datetime_str}"> <br>
            <br>
            <input type="submit" value="Submit">
            """
        html_string += """</form>""" 

        return html_string


# tb_name  = "2020年二季度.xlsx"
# data_1_listForRows = {
    #     "titles" : ["行号","项目号","子账户","账户名","分账户","账户名","受理人","金额"],
    #     "rows"   : {
    #         "data" :    [
    #                         {"行号":"733101", "项目号":"213123", "子账户":"A", "账户名":"XXXX", "分账户":"A1", "账户名":"XXXX",  "受理人":"小S", "金额": None},
    #                         {"行号":"733121", "项目号":"123123", "子账户":"A", "账户名":"XXXX", "分账户":"A1", "账户名":"XXXX",  "受理人":"小B", "金额":"321"},
    #                         {"行号":"733131", "项目号":"123123", "子账户":"B", "账户名":"YYYY", "分账户":"B1", "账户名":"YYYY 1","受理人":None, "金额":"123"},
    #                         {"行号":"733141", "项目号":"123123", "子账户":"B", "账户名":"YYYY", "分账户":None, "账户名":None,    "受理人":None, "金额":"123"},
    #                         {"行号":"733151", "项目号":"1231231","子账户":"B", "账户名":"YYYY", "分账户":"B3", "账户名":"YYYY 3","受理人":"小B", "金额": None}
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
