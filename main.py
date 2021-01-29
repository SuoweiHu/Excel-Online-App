from account import add_mockUsers

from app					import *
from routes_utils           import *
from routes_table_static    import *
from routes_table_dynamic   import *
from routes_table_setting   import *
from routes_file            import *
from routes_login           import *


def main():
	add_mockUsers() # 添加示范用户
	app.run(host='0.0.0.0', port=5000, debug=True)
	return

if __name__ == "__main__":
	main()
