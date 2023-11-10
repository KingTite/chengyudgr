# -*- coding=utf-8  -*-


import codecs
import json
import os


def del_space(orgfilepath):
    files = os.listdir(orgfilepath)
    for filename in files:
        if '.json' not in filename:
            continue
        with open(orgfilepath + '/' + filename, 'r') as f:
            file_data = json.loads(f.read())
        file_str = json.dumps(file_data, separators=(',', ':'), ensure_ascii=False)
        file_str.replace('\n', '')
        with codecs.open(orgfilepath + '/' + filename, 'w', 'utf-8') as f:
            f.write(file_str)




orgfilepath = './xxx'
del_space(orgfilepath)
