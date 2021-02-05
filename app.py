"""
Flask App 事例及其的一些设置
"""

from flask import Flask
import logging 
app = Flask(__name__)                           # FLASK INSTANCE
# 已经更改为在main文件设置日志等级
# logging.basicConfig(level=logging.DEBUG)      # DEBUG LEVEL LOGGING
# logging.basicConfig(level=logging.INFO)       # INFO  LEVEL LOGGING 
# app.config['MAXs_CONTENT_LENGTH'] = 5 * 1024 * 1024
app.config['SECRET_KEY'] = 'SAJHDKSAKJDHKJASHKJDKASDD'      



