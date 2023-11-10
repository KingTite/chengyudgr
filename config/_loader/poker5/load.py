# -*- coding: utf-8 -*-
'''
Created on 2016年7月27日

@author: zqh
'''

import os

from _loader import mainconf, mainhelper
from _loader.mainhelper import ftlog


def main():
    pokerdir = mainhelper.getPathInfo(__file__)[1]
    ftlog.info(pokerdir)
    # 重gdss获取数据
    mainconf.exportRedis('poker5:map.clientid', mainconf.CLIENTIDS)
    mainconf.exportRedis('poker5:map.productid', mainconf.PRODUCTIDS)
    mainconf.exportRedis('poker5:map.bieventid.new', mainconf.BIEVENTIDS)
    
    d1 = set(mainconf.OUT_REDIS['poker5:map.bieventid'].keys()) # json文件获取的数据
    d2 = set(mainconf.BIEVENTIDS.keys()) # GDSS 获取的数据
    d3 = d1 & d2
    ftlog.info('hall5 config d1-d3=', d1 -d3)
    ftlog.info('hall5 config d2-d3=', d2 -d3)
    
    sfs = os.listdir(pokerdir)
    for f in sfs:
        rkey, datas = mainhelper.readJsonData(pokerdir, f, 2)
        if rkey:
            mainconf.exportRedis(rkey, datas)

if __name__ == '__main__':
    mainconf.init()
    main()
