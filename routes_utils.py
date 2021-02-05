"""
路由实用工具，包括了:
- gen_dateTime_str  生成日期信息（用作提交时间）
- gen_operInfo_tup  生成操作员信息
- '/redirect'       跳转页面路由
"""

import datetime
from app import app
from flask import session, redirect, url_for

def gen_dateTime_str():
    """
    生成日期信息
    """
    now = datetime.datetime.now()

    # Day - transformation
    day = now.date()
    # day_str = day.__str__
    day_str = day.__format__('%y/%m/%d')

    # Time - transofmation
    time = now.time()
    # time_str = time.__str__
    time_str = time.strftime('%H:%M:%S')

    return f"{day_str} {time_str}"

def gen_operInfo_tup():
    """
    生成操作员信息
    """

    # Add form info into string 
    now = datetime.datetime.now()
    day = now.date()
    time = now.time()
    day_str = day.__format__('%Y/%m/%d')
    time_str = time.strftime('%H:%M:%S')
    datetime_str = day_str+ " " + time_str
    # print(datetime_str)
    operator_str = session["operator_name"]
    return (operator_str, datetime_str)

@app.route('/redirect', methods=["POST","GET"])
def redirect_to_index():
    """
    跳转到主页面, 或者指定页面
    """
    return redirect(url_for('index'))

    # if(session['previous_page'] is None):
    #     return redirect(url_for('index'))
    # else:
    #     prev_page = session['previous_page']
    #     session['previous_page'] = None
    #     return redirect(prev_page)

