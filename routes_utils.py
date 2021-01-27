import datetime
from app import app
from flask import session, redirect, url_for

# =============================================
# 生成日期信息/操作员信息
 
def gen_dateTime_str():
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

# =============================================
# 跳转页面

@app.route('/redirect', methods=["POST","GET"])
def redirect_to_index():
    """
    跳转到主页面, 或者指定页面
    """
    if(session['previous_page'] is None):
        return redirect(url_for('index'))
    else:
        prev_page = session['previous_page']
        session['previous_page'] = None
        return redirect(prev_page)

