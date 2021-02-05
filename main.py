from modules 		import add_mockUsers
from app			import *
from routes 		import *          


WEB_APP_PORT = '0.0.0.0'	# Web 应用访问的地址
WEB_ALL_HOST = 5000			# Web 应用访问的端口
DEBUG_MODE   = False 		# 如果想开启自动重启功能 + 日志设置为DEBUG等级 / 如果仅想看见INFO等级的日志

def main():
	add_mockUsers() 		# 添加示范用户
	app.run(host=WEB_APP_PORT, port=WEB_ALL_HOST, debug=DEBUG_MODE)	
	return

if __name__ == "__main__":
	main()
