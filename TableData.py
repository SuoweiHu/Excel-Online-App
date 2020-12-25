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

        tb_data = TableData(tb_name= tbname, titles=titles, rows=rows)
    """

    tb_name  = None
    titles   = None
    rows     = []

    def __init__(self, tb_name, titles, rows):
        """
        tb_name :   the file name here should be transferred into hashed prior to 
                    loggining into the database
        titles:     the titles of the table, should match with the max size of strings 
                    within a single row
        rows:       existing data of data rows, expecting a 2 dimentioanl array here, 
                    alike [[1,None,3], [None,3,4], [4,5,6]]. Where each sublist corresponds 
                    a row, and the sequence of data matches with the sequence of titles
        """
        self.tb_name    = tb_name   
        self.titles     = titles   
        self.rows       = rows
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
        return

    def to_dict(self):
        """
        为转化成JSON文件作准备, 转化后的数据类似如下
        transformed_dict = {
            "name": "2020年二季度"
            "titles" : ["行号","项目号","子账户","账户名","分账户","账户名","受理人","金额"],
            "rows"   : {
                "data" :    [
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
        table_dict["rows"]             = {"data":[], "operator":[]}
        table_dict["rows"]["data"]     = self.rows
        table_dict["rows"]["operator"] = self.operators
        return table_dict










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
