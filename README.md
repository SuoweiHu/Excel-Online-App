# 项目结构
```
./
	src/
		json/
		excel/
		temp/
	static/
		jQuery/
			...
		layui/
			...
	templates/
		...
	modules/
		__init__.py
		_Database_Utils.py
		_Database.py
		_ExcelVisitor.py
		_JsonVisitor.py
		_Hash_Utils.py
		account.py
	routes/
		__init__.py
		routes_utils.py
		routes_file.py
		routes_login.py
		routes_table_setting.py
		routes_table_static.py
		routes_table_dynamic.py
		debugTimer.py
	app.py
	main.py
```

部分目录/文件说明：
- `src...` 临时文件存储的文件夹
- `static` 网页使用资源的保存的位置，其中包括了lay-ui框架和jQuery
- `templates` flask自动渲染的html模版文件，若需要新增模版可以放在此目录下
- `modules`  内含所有和flask非相关的模组，其中包括数据库启动及其CURD操作，读取Excel/Json文件，临时存储表格数据的自定义类TableData等。
- `routes` 包含了所有的flask路由的模组。如果需要新增路由，请在该文件夹中新增文件，导入顶部目录的app.py作为应用实例，并在该文件夹中的\_\_init\_\_标示文件中import这个文件。如果需要更改访问路由的地址，请更改相关模组下对应的函数中@routes修饰器的路径。
- `app.py`全局的flask web app单例，被所有的路由模块所依赖
- `main.py` 应用的启动文件，包括了应用地址端口等设置


# “Modules” 目录/包
`__init__.py` 标识文件

`_ExcelVisitor.py`用于读取Excel文件为字典的模组

`_JsonVisitor.py`用于读取Json文件的为字典的模组

`_Hash_Utils.py`用于生成用户密码的哈希，表格的唯一文件\_ID使用

`_TableData.py`包含表格类TableData，用与临时存放从数据库获得的数据/从excel文件获得的数据，其中：
```
__init__:     从Json字典类型导入表格数据
toJson:       导出表格数据为Json字典，为入库作准备
get_row_id:   获得特定行在数据库中的ID
clear_column： 删除特定标题的某一列
```
注意其中的一些方法已被弃用，包括：
```
tableShow_toJson()
tableEdit_toJson()
tableShow_toHtml()
tableEdit_toHtml()
```
均为为被静态表格使用

`account.py` 用于添加模拟用户从而通过登陆界面执行登陆测试使用，现已改成通过数据接口登陆，所以不再使用该模组

`_Database.py`直接通过`PyMongo`模组操作数据库的模组，其中包含了两个类
1. `DB_Config`设置类，存储了一些静态变量为连接数据库时的默认设置
```
db_host           MongoDB 地址
db_port           MongoDB 端口
db_name           表格数据数据库
auth_db_name      认证数据库
auth_usr          用户名
auth_pass         密码
```
2. `MongoDatabase`类 创建`MongoClient`实例， 开启，关闭连接，上传，获取数据
```
start             开启连接
close             关闭连接
（以下为已连接后的操作）
insert            特定数据库特定集合添加文档
extract           ...获取文档
delete            ...删除文档
get_ids           获取集合中所有文档id
count_documents   ...文档数量
drop              删除集合
```

`_Database_Utils.py`所有数据库操作的Facade，对外向路由提供数据/接受变更，对内操作PyClient实例连接/关闭连接数据库/进行CRUD操作。其中`Database_Utils`类，根据功能分为了几个子类。相关的新的代码，请在其对应的业务逻辑的子类下添加。
1. `user`用户类
```
add... 新增
get... 获取
del... 删除
check_pass.... 检查密码是否正确
check_admin... 检查权限
gey_rows...    获得有权限的行号
```
2. `stat`统计类
```
completion  完成度
get...count 获取表格数量
```
3. `meta`表格元数据类
```
save... 新增
load... 获取
del.... 删除
pull... 获取（特定排序，特定数量）
```
4. `table`表格全量数据类
```
upload...     上传表格
load_table... 加载表格
save_table... 上传表格
get_tableTitles... 获取表格列标题 (DEPRECATED)
list_tableData_collections... 获取所有表格 (PARTIAL DEPRECATED)
```
5. `row`表格特定行数据类
```
get_table_row 获取特定行
set_table_row 更改特定行
count_table_row 返回符合条件的表格数量
```


# “routes” 目录/包
`__init__` 模块标示文件

`debugTimer.py` 使用flask自带`logger`在CLI中打印出带时间戳的DEBUG等级日志，仅为开发调试的时候使用。可以在`main.py`里更改日志等级，以过滤由此模组打印的日志。

`routes_login.py` 与用户登陆相关的路由，包括:
```
用户登陆时所用的路由， 包括了：
/               初始化session（登出），然后跳转到登陆页面
/index          若已经登陆跳转至主界面，否则跳转到登陆页面 '/'
/login          登陆界面
/api/login      处理登陆请求
```

`routes_file.py`  与上传文件相关的路由，包括:
```
/file                               上传文件
/file/select_IdReplAttribute        上传没有行号栏的文件
/update_success/<string:tb_name>    表格上传成功之后的跳转
```

`routes_utils.py` 路由实用工具，包括:
```
gen_dateTime_str  生成日期信息（用作提交时间）
gen_operInfo_tup  生成操作员信息
/redirect         跳转页面路由
```

`routes_table_setting` 用于设置表格元数据的路由，包括:
```
/select_RequredAttribute/<string:tb_name>/<string:return_aftFinish> 选择表格列的 “必填”, “预设可改” 的设置页面
/update_requiredTitles/<string:tb_name>                             上传更新的 “必填”, “预设可改” 的设置
/dueNComment/<string:tb_name>                                       截止日期/填表说明设置页面
/dueNComment_data_save/<string:tb_name>                             截止日期/填表说明设置上传
```

`routes_table_static.py` 使用layui静态数据表格（渲染普通html标签的表格为layui数据表格）的路由，包括：
```
/table/<string:option> ：         所有表格显示函数的Facade （作跳转到动态渲染的路由，不能删除）
table_main：                      展示所有表格统计数据（主界面）
table_show:                       编辑表格（编辑页面）
table_edit(_all) / table_submit： 提交行更改
table_clear                       删除表格 （不能删除）
```

`routes_table_dynamic.py` 使用layui动态数据表格（通过异步接口获得数据）的路由，包括:
```
/api/dataEdit                     编辑页面的数据接口
/api/dataMain/<string:option>     主界面的数据接口
/api/submit_row                   提交行的提交接口
/multiChoice/<string:tb_name>/<string:title>/<string:_id> 当点击预设单元格的显示函数
/submit_multiChoice               提交预设单元格
/api/toggle_archive               切换表格归档状态
/api/delete_table                 删除表格的请求路由
/main                             模版页面渲染 - 主界面
/edit/<string:table_name>         模版页面渲染  - 编辑界面
```


# 环境变更
**数据库：**
如果需要更改MongoDB数据库的地址和端口，请在MongoDB新建一个库用于存储表格数据，并为该库加上用户认证（可省，也可用其他库做认证，如启动时默认存在的admin库），接着在文件`modeules/_Database.py`里面更改`DB_Config`类中的默认设置，如下所示。

```python
db_host                    = 'mongodb'      # 地址
db_port        			   = 27017         	# 端口
db_name                    = 'TableData'    # 存表格数据的MongoDB数据库名称
auth_db_name               = 'TableData'    # 用于认证的数据库名称
auth_usr                   = 'yonghumin'    # 认证用户名
auth_pass                  = 'mima'   		# 认证密码
```

**Web应用：**
如果想更改Flask web app提供服务的地址，使得路由装饰器下的视图函数可以从另一个不同主机名的URL被访问（默认为 `0.0.0.0:5000`）；或者更改日志的等级/开启debug。那么你可以更改启动文件`main.py`下相关的全局变量，如下所示。

```python
WEB_APP_PORT = '0.0.0.0'	# Web 应用访问的地址
WEB_ALL_HOST = 5000			# Web 应用访问的端口
DEBUG_MODE   = False 		# 如果想开启自动重启功能 + 日志设置为DEBUG等级 / 如果仅想看见INFO等级的日志
```

**脚本：**
因为所有的框架用的都是本地的脚本，因此部署到线下的的时候不需要更改html文件里的`<script>`标签，如果需要更改重写框架原本的代码，也可以直接更改 static 下的相关文件。（例如想更改layui数据表格的行高可以在`static/layui/layui.css`中作如下更改）
```css
.layui-table-cell{
    height:      32px;
    line-height: 32px;
}
```
