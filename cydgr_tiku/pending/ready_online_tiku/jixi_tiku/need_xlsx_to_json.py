# -*- coding: utf8 -*-


import json
import codecs
import os
import sys
import xlrd


def Format(columtype, v):
    '''
    格式化字符串
    :param columtype: 
    :param v: 
    :return: 
    '''
    columvalue = ''
    if columtype == "int":
        columvalue = int(round(float(v)))
    elif columtype == 'float':
        columvalue = float(v)
    elif columtype == "string":
        columvalue = unicode(v)
    elif columtype == "list":
        columvalue = json.loads(v or [])  # eval(v or [])
    elif columtype == 'dict':
        columvalue = eval(v or {})
    return columvalue


def genCommonJson(val_type, title, sheet, nrows, ncols, json_file_name):
    print("-- ", json_file_name)
    json_list = []
    for rowindex in range(3, nrows):
        dic = {}
        for colindex in range(0, ncols):
            s = sheet.cell(rowindex, colindex).value
            # if s == 0:
            #     continue
            if colindex >= len(title):
                break
            # print(rowindex, colindex)
            dic[title[colindex]] = Format(val_type[colindex], s)
        json_list.append(dic)

    server_jsonpath = './json/' + json_file_name + '.json'  # 具体表修改
    try:
        with codecs.open(server_jsonpath, 'w', 'utf-8') as f:
            json.dump(json_list, f, indent=4, sort_keys=True, ensure_ascii=False)
    except:
        print(server_jsonpath, "->", json_list)


def genJson(file_name):

    data = xlrd.open_workbook(file_name)
    sheets_num = len(data.sheets())
    for i in range(0, sheets_num):
        sheet = data.sheet_by_index(i)
        nrows = sheet.nrows
        ncols = sheet.ncols
        json_file_name = sheet.name
        # 值类型
        val_type = []
        for i in range(0, ncols):
            val_type.append(sheet.cell(2, i).value)
        # 标题
        title = []
        for i in range(0, ncols):
            _str = sheet.cell(1, i).value
            if not _str:
                break
            title.append(sheet.cell(1, i).value)
        # 生成json
        genCommonJson(val_type, title, sheet, nrows, ncols, json_file_name)

def all_file_to_json(orgfilepath):
    files = os.listdir(orgfilepath)
    for filename in files:
        if 'win32' in sys.platform:
            filename = filename.decode('gbk')
        else:
            # mac
            filename = filename
        if '.xlsx' not in filename:
            continue
        genJson(orgfilepath + '/' + filename)


all_file_to_json('./xlsx')