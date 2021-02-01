
import sys
import pprint
from flask import config
from flask.config import Config
from pymongo import cursor
from pymongo.database import Database
from pymongo.mongo_client import MongoClient
from ._Database import MongoDatabase, DB_Config
from ._TableData import TableData
from ._Hash_Utils import hash_id


class Database_Utils:
    account_collection_name   = DB_Config.account_collection_name
    tableMeta_collection_name = DB_Config.tableMeta_collection_name
    noneData_collection_names = DB_Config.noneData_collection_names

    # ================================

    class user:
        # 获取用户信息 (全量返回)
        def get_user(name):
            config = DB_Config()
            db = MongoDatabase()
            db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
            _id = hash_id(name)
            user_dict = db.database[Database_Utils.account_collection_name].find_one({'_id':_id})
            db.close()
            return user_dict
        # 新增用户
        def add_user(name, password, rows, privilege='generic'):
            config = DB_Config()
            db = MongoDatabase()
            db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)

            # 生成用户唯一的ID
            _id      = hash_id(name)
            hash_password = hash_id(password)
            usr_dict = {'name':name, 'password':hash_password, 'privilege':privilege, 'rows':rows}

            # 如果已经存在用户则抛出错误 (可以后面改) 否则添加用户字典数据
            if(db.database[Database_Utils.account_collection_name].count_documents({'_id':_id}) == 1): 
                db.insert(collection=Database_Utils.account_collection_name, data=usr_dict, _id=_id)
                # raise(f"The account adding already exists : _id={_id}")
            else: db.insert(collection=Database_Utils.account_collection_name, data=usr_dict, _id=_id)

            db.close()
            return
        # 删除用户
        def del_user(name, password):
            config = DB_Config()
            db = MongoDatabase()
            db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)

            # 生成用户唯一的ID
            _id      = hash_id(name)
            hash_password = hash_id(password)

            if(db.database[Database_Utils.account_collection_name].count_documents({'_id':_id}) == 0): 
                db.close()
                return
                # raise(f"Your deleting account dont exist")
            else: 
                if(Database_Utils.user.check_password(name, password)):
                    col = db.database[Database_Utils.account_collection_name]
                    col.delete_one({'_id' : hash_id(name)})
                    db.close()
                    return 

            db.close()
            return
        # 强制删除用户
        def del_user_brutal(name):
            config = DB_Config()
            db = MongoDatabase()
            db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)

            # 生成用户唯一的ID
            _id      = hash_id(name)

            if(db.database[Database_Utils.account_collection_name].count_documents({'_id':_id}) == 0): 
                db.close()
                return
                # raise(f"Your deleting account dont exist")
            else: 
                col = db.database[Database_Utils.account_collection_name]
                col.delete_one({'_id' : hash_id(name)})
                db.close()
                return 

            db.close()
            return
        # 检查密码是否正确 
        def check_password(name, password):
            """
            返回true如果密码和数据库中的hash匹配
            """
            if((Database_Utils.user.get_user(name)) is None): return False
            return (Database_Utils.user.get_user(name))['password'] == hash_id(password)
        # 检查权限是否为admin
        def check_admin(name):
            """
            返回true如果用户的privilege字段为admin
            """
            return (Database_Utils.user.get_user(name))['privilege'] == 'admin'
        # 获得允许访问的行号列表
        def get_rows(name):
            """
            返回用户有权限访问的行
            """
            return (Database_Utils.user.get_user(name)['rows'])


    # ================================

    class stat:
        # HELPER: 得到必填列标题
        def get_mustFill_titles(tb_name):
            # 必填不包括任何的预设列，预设列：模版上传时有不为空的单元格的列
            # （因为可编辑的预设列会被标注为mustFill，所以需要在这里排除）
            table_meta = Database_Utils.meta.load_tablemMeta(tb_name=tb_name)
            mustfill_titles = table_meta['mustFill_titles'] 
            fixed_titles    = table_meta['fixed_titles']
            mustfill_titles = [title for title in mustfill_titles if title not in fixed_titles]
            return mustfill_titles
        # HELPER: 得到表格总行数
        def count_allRows(tb_name, is_admin=True, authorized_banknos=None):
            if(is_admin):
                # 通过元数据表获得信息
                return Database_Utils.meta.load_tablemMeta(tb_name=tb_name)['count'] + 1
            else:
                # 通过查询条件获得符合条件的文件数量
                bankno_list = [str(no) for no in authorized_banknos]
                query = {'data.行号':{'$in':bankno_list}}
                return Database_Utils.row.count_table_row(table_name=tb_name,query=query)
        # HELPER: 得到完成的表格行数
        def count_completedRows(tb_name, is_admin=True, authorized_banknos=None):
            mustFill_titles = Database_Utils.stat.get_mustFill_titles(tb_name=tb_name)  # 获取必填列标题
            if(is_admin):
                # 通过查询条件获得符合条件的文件数量
                sub_queries_1 = [{f'data.{title}':{'$ne':""}}   for title in mustFill_titles]
                sub_queries_2 = [{f'data.{title}':{'$ne':None}} for title in mustFill_titles]
                sub_queries = sub_queries_1 + sub_queries_2
                if(len(sub_queries) == 0): return Database_Utils.meta.load_tablemMeta(tb_name=tb_name)['count']
                return Database_Utils.row.count_table_row(table_name=tb_name,query={'$and':sub_queries})

            else:
                # 通过查询条件获得符合条件的文件数量
                bankno_list   = [str(no) for no in authorized_banknos]
                bankno_query  = {'data.行号':{'$in':bankno_list}}
                sub_queries_1 = [{f'data.{title}':{'$ne':""}}   for title in mustFill_titles]
                sub_queries_2 = [{f'data.{title}':{'$ne':None}} for title in mustFill_titles]
                sub_queries   = sub_queries_1 + sub_queries_2 + [bankno_query]
                print(sub_queries)
                if(len(sub_queries) == 0): return Database_Utils.meta.load_tablemMeta(tb_name=tb_name)['count']
                return Database_Utils.row.count_table_row(table_name=tb_name,query={'$and':sub_queries})

        # (DEPRECATED) HELPER: 得到表格完成行数   (admin)
        def deprecated_count_completedRows(config):
            """
            table name is filename without the .xlxs suffix
            for instance "2020年一季度"
            """

            # Store to database
            db = MongoDatabase()
            db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
            table_name = config.collection_name
            temp_mongoLoad = db.get_documents(collection=table_name, search_query=None)
            db.close()

            # Store to custom type
            table = TableData(json=temp_mongoLoad, tb_name=table_name)
            operators = table.operators

            meta             = Database_Utils.meta.load_tablemMeta(table_name)
            all_titles       = meta['titles']
            must_fill_titles = meta['mustFill_titles']
            fixed_titles     = set(meta['fixed_titles'])

            # 除去预设部分
            must_fill_titles = [item for item in must_fill_titles if item not in fixed_titles]

            count = 0
            for row, operator in zip(table.rows, table.operators):
                # if(operator[0] is not None) and (operator[1] is not None):
                cell_all_complted = True
                for title, cell in zip(all_titles,row): 
                    if(not cell_all_complted):break
                    if(title in must_fill_titles):
                        if(cell is None): cell_all_complted = False
                        else:
                            while(' ' in cell): cell = cell.replace(' ', '')
                            if(len(cell) == 0): cell_all_complted = False
                if(cell_all_complted): count += 1

            return count 
        # (DEPRECATED) HELPER: 得到表格完成百分比  (admin) 
        def deprecated_get_completionPercentage(tb_name=None, config=None):
            if(tb_name is not None) and (config is None):
                config = DB_Config()
                config.collection_name = tb_name.split('.')[0]
                config.tb_name         = tb_name.split('.')[0] + ".xlsx"
            elif(config is not None) and (tb_name is None):
                # config = config
                tb_name = config.collection_name
                pass
            else:
                raise("No input given (one of the tb_name, config must be filled)")

            c_comRow = Database_Utils.stat.deprecated_count_completedRows(config=config)
            c_allRow = Database_Utils.stat.count_allRows(tb_name=tb_name)

            return round(c_comRow/c_allRow * 100, 1)
        # (DEPRECATED) HELPER: 得到表格完成信息   (普通用户)
        def deprecated_get_completionState(config, authorized_banknos, key="行号"):
            """
            return (num_uncompleted, 
                    count_completed, 
                    num_uncompleted, 
                    completion_percentage, 
                    complted_status)
            """
            count_uncompleted = 0 
            count_all         = 0 

            table_name = config.collection_name
            db = MongoDatabase()
            db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
            temp_mongoLoad = db.get_documents(collection=table_name)
            db.close()

            meta             = Database_Utils.meta.load_tablemMeta(table_name)
            all_titles       = meta['titles'] 
            must_fill_titles = meta['mustFill_titles']
            fixed_titles     = set(meta['fixed_titles'])

            # 除去预设部分
            must_fill_titles = [item for item in must_fill_titles if item not in fixed_titles]


            for bankno in authorized_banknos:
                bankno = str(bankno)
                table = TableData(json=temp_mongoLoad, tb_name=table_name)
                bankno_index = table.titles.index(key)
                for i in range (len(table.rows)):
                    row = table.rows[i]
                    if(row[bankno_index] == bankno):
                        count_all += 1 

                        # # 如果还没有用户填过那就肯定未完成这行
                        # if(table.operators[i][0] is None):
                        #     count_uncompleted += 1

                        # # 如果有用户填过则检车是否所有行都已经完成
                        # else:
                        cell_all_complted = True
                        for title, cell in zip(all_titles,row):
                            if(not cell_all_complted):break
                            if(title in must_fill_titles):
                                if(cell is None):cell_all_complted = False
                                else:
                                    while(' ' in cell): cell = cell.replace(' ', '')
                                    if(len(cell) == 0): cell_all_complted = False
                                    
                        if(not cell_all_complted): count_uncompleted += 1

            # print(count_all)
            # print(count_uncompleted)

            # Return check result
            count_completed = (count_all-count_uncompleted)
            if(count_all == 0): percentage = 100.0
            else: percentage = round(count_completed/count_all * 100, 1)
            return (count_uncompleted,
                    count_completed,
                    count_all,
                    percentage,
                    count_completed==count_all)
        
        # 得到表格完成度信息
        def completion(tb_name, is_admin=True, authorized_banknos=None):
            rtn_completion  = {}  # 最终返回的完成度字典
            rtn_completion['completed']   = Database_Utils.stat.count_completedRows(tb_name=tb_name, is_admin=is_admin,authorized_banknos=authorized_banknos) # 获取用户的完成（有权限的）行数
            rtn_completion['total']       = Database_Utils.stat.count_allRows(tb_name=tb_name,is_admin=is_admin,authorized_banknos=authorized_banknos) # 获取用户的所有（有权限的）行数
            rtn_completion['uncompleted'] = rtn_completion['total'] - rtn_completion['completed']
            if(rtn_completion['total'] != 0): rtn_completion['percentage']  = round(rtn_completion['completed']/rtn_completion['total'], 2) # 完成百分比（2位小数点）
            else: rtn_completion['percentage'] = 1.00
            return rtn_completion

    class meta:
        # 存储特定表格的元数据
        def save_tablemMeta(tb_name, meta):
            """
            保存表格的元数据, 包含:
                表格的名字,
                表格的总行书,    
                表格的所有标题,
                表格的预设列标题, 
                表格的必填列标题, (可以更改)

            Parameter:
                tb_name: 表格名称 (将会被用来生成_id)
                meta:    表格元数据
            """
            tb_name = tb_name.split('.')[0]
            tb_name = tb_name.replace(' ','')
            db = MongoDatabase()
            db.start()
            db.insert(collection=Database_Utils.tableMeta_collection_name,\
                data=meta, _id=str(hash_id(tb_name)))
            db.close()
        # 读取特定表格的元数据
        def load_tablemMeta(tb_name):
            """
            保存表格的元数据, 包含:
                表格的名字,
                表格的总行书,    
                表格的所有标题,
                表格的预设列标题, 
                表格的必填列标题, (可以更改)

            Parameter:
                tb_name: 表格名称 (将会被用来生成_id)
            """
            tb_name = tb_name.split('.')[0]
            tb_name = tb_name.replace(' ','')
            db = MongoDatabase()
            db.start()
            rtn = db.get_documents(collection=Database_Utils.tableMeta_collection_name,\
                search_query={'tb_name':tb_name})
            rtn = rtn[0]
            db.close()

            return rtn
        #  删除特定表格的元数据
        def del_tablemMeta(tb_name):
            tb_name = tb_name.split('.')[0]
            tb_name = tb_name.replace(' ','')
            db = MongoDatabase()
            db.start()
            db.delete(collection=Database_Utils.tableMeta_collection_name,query={'tb_name' : tb_name})
            db.close()


    # ================================

    class table:
        # 提交模版 
        def upload_table(name, data):
            config= DB_Config(tb_name=name, collection_name=name.split('.')[0])
            db = MongoDatabase()
            db.start(host=config.db_host, port=config.db_port, name=config.db_name, clear=False)
            for row in data.items():
                db.insert(collection=name, data=row[1], _id=row[0])
            db.close()
            return
        # 读取表格
        def load_table(tb_name, search_query=None, sort=(None,None)):
            # if(tb_name is not None) and (config is None):
            #     config = DB_Config()
            #     config.collection_name = tb_name.split('.')[0]
            #     config.tb_name         = tb_name.split('.')[0] + ".xlsx"
            # elif(config is not None) and (tb_name is None):pass
            # else:raise("No input given (one of the tb_name, config must be filled)")

            table_name = tb_name
            config = DB_Config()
            db = MongoDatabase()
            db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
            
            if(search_query is None):
                temp_mongoLoad = db.get_documents(collection=table_name)
            else:
                temp_cursor = db.get_documents(collection=table_name, search_query=search_query, sort=sort)
                temp_mongoLoad = {}
                for item in temp_cursor:
                    keys = list(item)
                    keys.remove('_id')
                    item_id = item['_id']
                    del item['_id']
                    temp_mongoLoad[item_id] = item
            db.close()

            table = TableData(json=temp_mongoLoad, tb_name=table_name)
            return table

        # 保存变更
        def save_table(tb_name,data):
            config = None
            if(tb_name is not None) and (config is None):
                config = DB_Config()
                config.collection_name = tb_name.split('.')[0]
                config.tb_name         = tb_name.split('.')[0] + ".xlsx"
            elif(config is not None) and (tb_name is None):pass
            else:raise("No input given (one of the tb_name, config must be filled)")

            db = MongoDatabase()
            db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
            # db.drop(collection=config.collection_name)
            for row in data.items():
                db.insert(collection=tb_name, data=row[1], _id=row[0])
            db.close()
            return 
        # 读取特定表格的列标题
        def get_tableTitles(tb_name):
            # config = None
            # if(tb_name is not None) and (config is None):
            #     config = DB_Config()
            #     config.collection_name = tb_name.split('.')[0]
            #     config.tb_name         = tb_name.split('.')[0] + ".xlsx"
            # elif(config is not None) and (tb_name is None):pass
            # else:raise("No input given (one of the tb_name, config must be filled)")

            table_name = tb_name
            config = DB_Config(collection_name=tb_name)
            db = MongoDatabase()
            db.start(host=config.db_host, port=config.db_port, name=config.db_name,clear=False)
            temp_mongoLoad = db.get_documents(collection=table_name)
            db.close()

            table = TableData(json=temp_mongoLoad, tb_name=table_name)
            titles = table.titles
            return titles
        # 读取所有的表格名字
        def list_tableData_collections():
            db = MongoDatabase()
            db.start()
            collection_names = db.list_tableData_collectionNames()
            db.close()
            return collection_names
    
    class row:
        # 获得表格特定行 (通过行在collection中的document id)
        def get_table_row(table_name, row_id):
            """
            table_name: 表格名, 数据库中对应一个集合
            row_id:     行uuid, 数据库中对应刚刚集合中的一个文件
            return:     整个文件 (包含其id, 需自行去除)
            """

            db_config = DB_Config()
            db = MongoDatabase()
            db.start(host=db_config.db_host, port=db_config.db_port, name=db_config.db_name,clear=False)
            rtn = db.database[table_name].find_one({'_id':row_id})
            db.close()
            return rtn
        # 更改表格行 (通过行在collection中的document id)
        def set_table_row(table_name, row_id, data):
            """
            table_name: 表格名, 数据库中对应一个集合
            row_id:     行uuid, 数据库中对应刚刚集合中的一个文件
            return:     整个文件 (包含其id, 需自行去除)
            """
            db_config = DB_Config()
            db = MongoDatabase()
            db.start(host=db_config.db_host, port=db_config.db_port, name=db_config.db_name,clear=False)
            # db.database[table_name].delete_one({'_id':row_id})
            # db.database[table_name].insert_one(data)
            db.database[table_name].update_one({'_id':row_id}, {'$set': data})
            db.close()
            return 
        # 返回符合条件的表格数量
        def count_table_row(table_name, query={}):
            """
            table_name: 表格名, 数据库中对应一个集合
            row_id:     行uuid, 数据库中对应刚刚集合中的一个文件
            return:     整个文件 (包含其id, 需自行去除)
            """

            db_config = DB_Config()
            db = MongoDatabase()
            db.start(host=db_config.db_host, port=db_config.db_port, name=db_config.db_name,clear=False)
            rtn = db.database[table_name].count_documents(query)
            db.close()
            return rtn

    # ================================
    



