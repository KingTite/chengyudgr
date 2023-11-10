# -*- coding: utf-8 -*-
'''
Created on 2017年4月24日

@author: zqh
'''
import urllib2
import urllib
import json
import sys
import os


def main():
    fcid = '20016'  # sys.argv[1]
    tcid = '20543'  # sys.argv[2]

    basepath = os.path.abspath(__file__)
    basepath = os.path.dirname(basepath)
    basepath = os.path.normpath(basepath + './../game')
    print basepath

    for d1 in os.listdir(basepath):
        d1 = basepath + '/' + d1
        if not os.path.isdir(d1):
            continue
        print d1
        for d2 in os.listdir(d1):
            d2 = d1 + '/' + d2
            # print d2
            vc = d2 + '/vc.json'
            if os.path.isfile(vc):
                print vc
                f = open(vc, 'r')
                datas = json.load(f)
                f.close()
                if fcid in datas:
                    datas[tcid] = datas[fcid]
                    f = open(vc, 'w')
                    f.write(json.dumps(datas,  ensure_ascii=True, indent=4, sort_keys=True))
                    f.close()


if __name__ == '__main__':
    main()
