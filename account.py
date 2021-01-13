from modules._Database_Utils import Database_Utils
from modules._Hash_Utils import hash_id

# 添加账号
def add_account(name, password, rows, privilege='generic'):
    """
    添加账号
    name:      string  
    password:  string 
    rows:      1|n * int32
    privilege  'generic' | 'admin'
    """
    Database_Utils.user.add_user(name=name,password=password,rows=rows, privilege=privilege)
    return

# 删除账号
def del_account(name, password):
    """
    删除账号
    """
    Database_Utils.user.del_user(name, password)
    return

# 添加示范用户
def add_mockUsers():
    user_rows = [
        {'name':'733101',       'privilege':'generic',     'password': '733101',            'rows':[733101]},
        {'name':'733121',       'privilege':'generic',     'password': '733121',            'rows':[733121]},
        {'name':'733131',       'privilege':'generic',     'password': '733131',            'rows':[733131]},
        {'name':'733141',       'privilege':'generic',     'password': '733141',            'rows':[733141]},
        {'name':'733151',       'privilege':'generic',     'password': '733151',            'rows':[733151]},
        {'name':'admin' ,       'privilege':'admin',       'password': 'admin',             'rows':[]},
        {'name':'填报用户',      'privilege':'generic',     'password':'tianbaoyonghu',       'rows':[733101]},
        {'name':'上传模板',      'privilege':'admin',       'password':'shangchuanmoban',     'rows':[]},
    ]
    for user in user_rows:
        add_account(name=user['name'],password=user['password'],rows=user['rows'],privilege=user['privilege'])
    return





