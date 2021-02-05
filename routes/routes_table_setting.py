"""
处理表格设置的路由，包括了：
- /select_RequredAttribute/<string:tb_name>/<string:return_aftFinish> 选择表格列的 “必填”, “预设可改” 的设置页面
- /update_requiredTitles/<string:tb_name>                             上传更新的 “必填”, “预设可改” 的设置
- /dueNComment/<string:tb_name>                                       截止日期/填表说明设置页面
- /dueNComment_data_save/<string:tb_name>                             截止日期/填表说明设置上传
"""
from modules._Database_Utils import Database_Utils
from app                    import app
from flask                  import Flask, config, render_template, flash, make_response, send_from_directory, redirect, url_for, session, request
from .routes_utils           import *
from .routes_file            import *
from .debugTimer             import *

# 选择表格列的 “必填”, “预设可改” 的设置页面
@app.route('/select_RequredAttribute/<string:tb_name>/<string:return_aftFinish>', methods=['GET'])
def select_RequredAttribute(tb_name, return_aftFinish):
    app.logger.info(f'访问表格必填预设可改的设置页面, table:{tb_name}')
    titles = Database_Utils.table.get_tableTitles(tb_name=tb_name)
    meta = Database_Utils.meta.load_tablemMeta(tb_name=tb_name)
    return render_template("table_option_selectRequiredAttribute.html",\
        table_name = tb_name,\
        table_titles         = titles,\
        table_fixedTitles    = meta['fixed_titles'],\
        table_requiredTitles = meta['mustFill_titles'],\
        request_url = "/update_requiredTitles",\
        return_aftFinish = return_aftFinish,
        # finish_directURL = url_for('upload_successRedirect',tb_name=tb_name),
        finish_directURL = f"/upload_success/{tb_name}",\
    )

# 上传更新的 “必填”, “预设可改” 的设置
@app.route('/update_requiredTitles/<string:tb_name>', methods=['POST'])
def route_upload_requiredTitles(tb_name):
    app.logger.info(f'提交表格必填预设可改的设置, table:{tb_name}')
    meta = Database_Utils.meta.load_tablemMeta(tb_name=tb_name)
    meta['mustFill_titles'] = [item_key for item_key,_ in dict(request.form).items()]

    # # 获取表格原来的meta
    # updated_meta  = dict(request.form.get('meta'))
    # original_meta = Database_Utils.meta.load_tablemMeta(tb_name=tb_name)
    # meta = {}

    # # 替换被更新的字段
    # for attri,value in original_meta.items():
    #     if(attri in list(updated_meta.keys())):meta[attri] = updated_meta[attri]
    #     else:meta[attri] = value

    # # 上传更新后的文件
    Database_Utils.meta.save_tablemMeta(tb_name=tb_name, meta=meta)

    # return "Successful !"
    return redirect(url_for('edit_specified_table', table_name=tb_name))

# 截止日期/填表说明设置页面
@app.route('/dueNComment/<string:tb_name>')
def fill_dueDate_n_comment(tb_name):
    app.logger.info(f'访问表格 截止日期/填表说明设置页面, table:{tb_name}')
    meta = Database_Utils.meta.load_tablemMeta(tb_name=tb_name)
    if('comment' in meta.keys()): comment = meta['comment']
    else: comment = ""
    if('due' in meta.keys()): due = meta['due']
    else: due = ""

    return render_template('table_option_dueNcomment.html',
        request_url = "/dueNComment_data_save",\
        table_name  = tb_name,
        finish_directURL = '/table/all',
        comment = comment,
        due = due
    )
    
# 截止日期/填表说明设置上传
@app.route('/dueNComment_data_save/<string:tb_name>',methods=["POST","GET"])
def save_dueDate_n_comment(tb_name):
    app.logger.info(f'提交表格 截止日期/填表说明设置, table:{tb_name}')
    meta = Database_Utils.meta.load_tablemMeta(tb_name=tb_name)
    # meta['comment']= request.form.get('comment')
    # meta['due']    = request.form.get('due')
    meta['comment']= request.args.get('comment')
    meta['due']    = request.args.get('date')
    if(meta['due'] is None): meta['due']=""
    Database_Utils.meta.save_tablemMeta(tb_name=tb_name,meta=meta)
    return redirect('/table/all')


