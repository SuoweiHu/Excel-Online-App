"""
添加/删除(假)账号
"""

from modules._Database_Utils import Database_Utils
from modules._Hash_Utils import hash_id

# 添加账号
def add_account(name, nickname, password, rows, privilege='generic'):
    """
    添加账号
    name:      string  
    password:  string 
    rows:      1|n * int32
    privilege  'generic' | 'admin'
    """
    Database_Utils.user.add_user(name=name,nickname=nickname, password=password,rows=rows, privilege=privilege)
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
        # Admin & template 
        {'name':'admin' ,   'nickname':'n_name_admin' ,      'privilege':'admin',       'password': 'admin',             'rows':[]},
        {'name':'填报用户',   'nickname':'n_name_填报用户',     'privilege':'generic',     'password':'tianbaoyonghu',       'rows':[733101]},
        {'name':'上传模板',   'nickname':'n_name_上传模板',     'privilege':'admin',       'password':'shangchuanmoban',     'rows':[]},
        # {'name':'XXXXXXXXXX', 'nickname':'XXXXXXXXXXXX', 'privilege':'generic', 'password': 'XXXXXXXXXXXX', 'rows':[]},

        # DEMO purpose 
        # {'name':'733101',  'nickname':'n_name_733101',  'privilege':'generic', 'password': '733101', 'rows':[733101]},
        # {'name':'733121',  'nickname':'n_name_733121',  'privilege':'generic', 'password': '733121', 'rows':[733121]},
        # {'name':'733131',  'nickname':'n_name_733131',  'privilege':'generic', 'password': '733131', 'rows':[733131]},
        # {'name':'733141',  'nickname':'n_name_733141',  'privilege':'generic', 'password': '733141', 'rows':[733141]},
        # {'name':'733151',  'nickname':'n_name_733151',  'privilege':'generic', 'password': '733151', 'rows':[733151]},

        # Real users 
        # 杭州
        {'name':'733011', 'nickname':'杭州分行账务中心', 'privilege':'generic', 'password': '733011', 'rows':[733011]},
        {'name':'733101', 'nickname':'杭州风寒营业部', 'privilege':'generic', 'password': '733101', 'rows':[733101]},
        {'name':'733111', 'nickname':'杭州天水支行', 'privilege':'generic', 'password': '733111', 'rows':[733111]},
        {'name':'733121', 'nickname':'杭州凤起支行', 'privilege':'generic', 'password': '733121', 'rows':[733121]},
        {'name':'733161', 'nickname':'杭州西湖支行', 'privilege':'generic', 'password': '733161', 'rows':[733161]},
        {'name':'733171', 'nickname':'杭州钱江支行', 'privilege':'generic', 'password': '733171', 'rows':[733171]},
        {'name':'733191', 'nickname':'杭州平海支行', 'privilege':'generic', 'password': '733191', 'rows':[733191]},
        {'name':'733211', 'nickname':'杭州延安支行', 'privilege':'generic', 'password': '733211', 'rows':[733211]},
        {'name':'733221', 'nickname':'杭州钱塘支行', 'privilege':'generic', 'password': '733221', 'rows':[733221]},
        {'name':'733251', 'nickname':'杭州玉泉支行', 'privilege':'generic', 'password': '733251', 'rows':[733251]},
        {'name':'733261', 'nickname':'杭州庆春支行', 'privilege':'generic', 'password': '733261', 'rows':[733261]},
        {'name':'733271', 'nickname':'杭州省府路支行', 'privilege':'generic', 'password': '733271', 'rows':[733271]},
        {'name':'733281', 'nickname':'杭州湖墅支行', 'privilege':'generic', 'password': '733281', 'rows':[733281]},
        {'name':'733291', 'nickname':'杭州经济技术开发区支行', 'privilege':'generic', 'password': '733291', 'rows':[733291]},
        {'name':'753011', 'nickname':'杭州四季青小微企业专营支行', 'privilege':'generic', 'password': '753011', 'rows':[753011]},
        {'name':'753021', 'nickname':'杭州城西支行', 'privilege':'generic', 'password': '753021', 'rows':[753021]},
        {'name':'753041', 'nickname':'杭州吴山支行', 'privilege':'generic', 'password': '753041', 'rows':[753041]},
        {'name':'733131', 'nickname':'杭州萧山支行', 'privilege':'generic', 'password': '733131', 'rows':[733131]},
        {'name':'733061', 'nickname':'杭州临江支行', 'privilege':'generic', 'password': '733061', 'rows':[733061]},
        {'name':'733181', 'nickname':'杭州之江支行', 'privilege':'generic', 'password': '733181', 'rows':[733181]},
        {'name':'733201', 'nickname':'杭州江东支行', 'privilege':'generic', 'password': '733201', 'rows':[733201]},
        {'name':'733241', 'nickname':'杭州滨江支行', 'privilege':'generic', 'password': '733241', 'rows':[733241]},
        {'name':'753161', 'nickname':'杭州江南支行', 'privilege':'generic', 'password': '753161', 'rows':[753161]},
        {'name':'733141', 'nickname':'杭州余杭支行', 'privilege':'generic', 'password': '733141', 'rows':[733141]},
        {'name':'133081', 'nickname':'杭州未来科技城支行', 'privilege':'generic', 'password': '133081', 'rows':[133081]},
        {'name':'733231', 'nickname':'杭州九堡支行', 'privilege':'generic', 'password': '733231', 'rows':[733231]},
        {'name':'753211', 'nickname':'杭州海创科技园支行', 'privilege':'generic', 'password': '753211', 'rows':[753211]},
        {'name':'733151', 'nickname':'杭州富阳支行', 'privilege':'generic', 'password': '733151', 'rows':[733151]},
        {'name':'753261', 'nickname':'杭州大源小微企业专营支行', 'privilege':'generic', 'password': '753261', 'rows':[753261]},
        {'name':'733071', 'nickname':'杭州桐庐支行', 'privilege':'generic', 'password': '733071', 'rows':[733071]},
        {'name':'753031', 'nickname':'杭州建德支行', 'privilege':'generic', 'password': '753031', 'rows':[753031]},
        # 嘉兴
        {'name':'733301', 'nickname':'嘉兴分行营业部', 'privilege':'generic', 'password': '733301', 'rows':[733301]},
        {'name':'733311', 'nickname':'嘉兴海宁支行', 'privilege':'generic', 'password': '733311', 'rows':[733311]},
        {'name':'733331', 'nickname':'嘉兴平湖支行', 'privilege':'generic', 'password': '733331', 'rows':[733311]},
        {'name':'733351', 'nickname':'嘉兴南湖支行', 'privilege':'generic', 'password': '733351', 'rows':[733351]},
        {'name':'733361', 'nickname':'嘉兴秀洲支行', 'privilege':'generic', 'password': '733361', 'rows':[733361]},
        {'name':'733371', 'nickname':'嘉兴桐乡支行', 'privilege':'generic', 'password': '733371', 'rows':[733371]},
        {'name':'733381', 'nickname':'嘉兴嘉善支行', 'privilege':'generic', 'password': '733381', 'rows':[733381]},
        {'name':'733391', 'nickname':'嘉兴海盐支行', 'privilege':'generic', 'password': '733391', 'rows':[733391]},
        {'name':'753301', 'nickname':'嘉兴经济技术开发区支行', 'privilege':'generic', 'password': '753301', 'rows':[753301]},
        # 绍兴
        {'name':'733041', 'nickname':'绍兴分行财务中心', 'privilege':'generic', 'password': '733041', 'rows':[733041]},
        {'name':'733401', 'nickname':'绍兴分行营业部', 'privilege':'generic', 'password': '733401', 'rows':[733401]},
        {'name':'733411', 'nickname':'绍兴上虞支行', 'privilege':'generic', 'password': '733411', 'rows':[733411]},
        {'name':'733421', 'nickname':'绍兴城中支行', 'privilege':'generic', 'password': '733421', 'rows':[733421]},
        {'name':'733431', 'nickname':'绍兴城东支行', 'privilege':'generic', 'password': '733431', 'rows':[733431]},
        {'name':'733441', 'nickname':'绍兴越城支行', 'privilege':'generic', 'password': '733441', 'rows':[733441]},
        {'name':'733451', 'nickname':'绍兴城北支行', 'privilege':'generic', 'password': '733451', 'rows':[733451]},
        {'name':'733461', 'nickname':'绍兴轻纺城支行', 'privilege':'generic', 'password': '733461', 'rows':[733461]},
        {'name':'733471', 'nickname':'绍兴诸暨支行', 'privilege':'generic', 'password': '733471', 'rows':[733471]},
        {'name':'733481', 'nickname':'绍兴嵊州支行', 'privilege':'generic', 'password': '733481', 'rows':[733481]},
        {'name':'733491', 'nickname':'绍兴新昌支行', 'privilege':'generic', 'password': '733491', 'rows':[733491]},
        {'name':'733051', 'nickname':'温州分行账务中心', 'privilege':'generic', 'password': '733051', 'rows':[733051]},
        {'name':'733501', 'nickname':'温州分行营业部', 'privilege':'generic', 'password': '733501', 'rows':[733501]},
        {'name':'733511', 'nickname':'温州瓯海支行', 'privilege':'generic', 'password': '733511', 'rows':[733511]},
        {'name':'733521', 'nickname':'温州乐清支行', 'privilege':'generic', 'password': '733521', 'rows':[733521]},
        {'name':'733541', 'nickname':'温州柳市支行', 'privilege':'generic', 'password': '733541', 'rows':[733541]},
        {'name':'733551', 'nickname':'温州瑞安支行', 'privilege':'generic', 'password': '733551', 'rows':[733551]},
        {'name':'733571', 'nickname':'温州鹿城支行', 'privilege':'generic', 'password': '733571', 'rows':[733571]},
        {'name':'733581', 'nickname':'温州经济开发区支行', 'privilege':'generic', 'password': '733581', 'rows':[733581]},
        {'name':'733591', 'nickname':'温州龙湾支行', 'privilege':'generic', 'password': '733591', 'rows':[733591]},
        {'name':'733891', 'nickname':'温州人民路支行', 'privilege':'generic', 'password': '733891', 'rows':[733891]},
        {'name':'753501', 'nickname':'温州苍南支行', 'privilege':'generic', 'password': '753501', 'rows':[753501]},
        # 义乌
        {'name':'733801', 'nickname':'义乌分行营业部', 'privilege':'generic', 'password': '733801', 'rows':[733801]},
        {'name':'733811', 'nickname':'义乌篁园支行', 'privilege':'generic', 'password': '733811', 'rows':[733811]},
        {'name':'733821', 'nickname':'义乌北苑支行', 'privilege':'generic', 'password': '733821', 'rows':[733821]},
        {'name':'757011', 'nickname':'义乌北苑支行', 'privilege':'generic', 'password': '757011', 'rows':[757011]},
        {'name':'757031', 'nickname':'义乌稠城小微企业专营支行', 'privilege':'generic', 'password': '757031', 'rows':[757031]},
        {'name':'757041', 'nickname':'义乌福田小微企业专营支行', 'privilege':'generic', 'password': '757041', 'rows':[757041]},
        # 金华
        {'name':'757091', 'nickname':'金华分行营业部', 'privilege':'generic', 'password': '757091', 'rows':[757091]},
        {'name':'733831', 'nickname':'金华永康支行', 'privilege':'generic', 'password': '733831', 'rows':[733831]},
        {'name':'733841', 'nickname':'金华东阳支行', 'privilege':'generic', 'password': '733841', 'rows':[733841]},
        {'name':'757121', 'nickname':'金华武义支行', 'privilege':'generic', 'password': '757121', 'rows':[757121]},
        # 丽水
        {'name':'733851', 'nickname':'丽水分行营业部', 'privilege':'generic', 'password': '733851', 'rows':[733851]},
        {'name':'733861', 'nickname':'丽水缙云支行', 'privilege':'generic', 'password': '733861', 'rows':[733861]},
        {'name':'733871', 'nickname':'丽水青田支行', 'privilege':'generic', 'password': '733871', 'rows':[733871]},
        # 湖州
        {'name':'733901', 'nickname':'湖州支行', 'privilege':'generic', 'password': '733901', 'rows':[733901]},
        {'name':'733911', 'nickname':'湖州安吉支行', 'privilege':'generic', 'password': '733911', 'rows':[733911]},
        {'name':'733921', 'nickname':'湖州长兴支行', 'privilege':'generic', 'password': '733921', 'rows':[733921]},
        {'name':'733931', 'nickname':'湖州德清支行', 'privilege':'generic', 'password': '733931', 'rows':[733931]},
        # 台州
        {'name':'733951', 'nickname':'台州分行营业部', 'privilege':'generic', 'password': '733951', 'rows':[733951]},
        {'name':'733961', 'nickname':'台州路桥支行', 'privilege':'generic', 'password': '733961', 'rows':[733961]},
        {'name':'733971', 'nickname':'台州三门支行', 'privilege':'generic', 'password': '733971', 'rows':[733971]},
        {'name':'733981', 'nickname':'台州温岭支行', 'privilege':'generic', 'password': '733981', 'rows':[733981]},
        {'name':'733991', 'nickname':'台州黄岩支行', 'privilege':'generic', 'password': '733991', 'rows':[733991]},
        {'name':'757161', 'nickname':'台州玉环支行', 'privilege':'generic', 'password': '757161', 'rows':[757161]},
        {'name':'757171', 'nickname':'台州临海支行', 'privilege':'generic', 'password': '757171', 'rows':[757171]},
        # 舟山 / 衢州
        {'name':'757201', 'nickname':'舟山分行营业部', 'privilege':'generic', 'password': '757201', 'rows':[757201]},
        {'name':'757211', 'nickname':'舟山沈家门小微企业专营支行', 'privilege':'generic', 'password': '757211', 'rows':[757211]},
        {'name':'757301', 'nickname':'衢州分行营业部', 'privilege':'generic', 'password': '757301', 'rows':[757301]},
    ]
    for user in user_rows:
        add_account(name=user['name'],nickname=user['nickname'] , password=user['password'],rows=user['rows'],privilege=user['privilege'])
    return





