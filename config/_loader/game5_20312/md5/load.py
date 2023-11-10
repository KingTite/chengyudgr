# -*- coding: utf-8 -*-
'''
Created on 2016年7月27日

@author: zqh
'''
import os
import json
from _loader import mainconf, mainhelper
from _loader.mainhelper import ftlog

def main():

    d = os.path.dirname(__file__)
    parent_path = os.path.dirname(d)

    md5dict = {}
    for i in os.listdir(parent_path):
        temp_dir = os.path.join(parent_path, i)
        if os.path.isdir(temp_dir):
            tfile = __file__.replace('md5', os.path.basename(temp_dir))
            cm = mainconf.getTcVcDatasGame(tfile)
            # mainconf.exportRedis(cm.scKey, cm.scDatas)

            md5 = mainhelper.md5digest(json.dumps(cm.scDatas))
            ftlog.debug('main md5',
                        'key=', cm.scKey,
                        'temp_dir', temp_dir,)
            if os.path.basename(temp_dir) != 'md5':
                md5dict[os.path.basename(temp_dir)] = md5

    mainconf.exportRedis('game5:20312:md5:sc', md5dict)

    print parent_path

if __name__ == '__main__':
    mainconf.init()
    main()