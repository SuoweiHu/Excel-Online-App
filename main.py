from modules 		import add_mockUsers
from app			import *
from routes 		import *          


WEB_APP_PORT = '0.0.0.0'
WEB_ALL_HOST = 5000
DEBUG_MODE   = False

def main():
	add_mockUsers() 								 # 添加示范用户
	# app.run(host='0.0.0.0', port=5000, debug=True) # 如果想开启自动重启功能 + 日志设置为DEBUG等级
	app.run(host='0.0.0.0', port=5000, debug=False)	 # 如果仅想看见INFO等级的日志
	return

if __name__ == "__main__":
	main()
