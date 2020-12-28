class Config:

    def __init__(self, tb_name=None, db_host=None, db_port=None, db_name=None, collection_name=None):
        # Default Values for config
        self.tb_name = ''           #'2020年二季度.xlsx'
        self.db_host = 'localhost'
        self.db_port = 27017
        self.db_name = '账户统计'
        self.collection_name = ''   #'2020第二季度'  

        # Custom Valus for config
        if(tb_name is not None): self.tb_name = tb_name  # 注意这里的文件名是带后缀的: 2020第一季度.xlsx     
        if(db_host is not None): self.db_host = db_host 
        if(db_port is not None): self.db_port = db_port
        if(db_name is not None): self.db_name = db_name
        if(collection_name is not None): self.collection_name = collection_name # 里的文件名是不带后缀的: 2020第一季度

        return

