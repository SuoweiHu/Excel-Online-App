from routes import app
from account import add_mockUsers

def main():
    add_mockUsers() # 添加示范用户
    app.run(host='0.0.0.0', port=5000, debug=True)
    return

if __name__ == "__main__":
    main()
