# -*- coding: utf-8 -*-
'''
Created on 2016年7月27日

@author: zqh
'''

from _loader import mainconf

def main():
    cm = mainconf.getTcVcDatasGame(__file__)
    mainconf.exportRedis(cm.scKey, cm.scDatas)

if __name__ == '__main__':
    mainconf.init()
    main()