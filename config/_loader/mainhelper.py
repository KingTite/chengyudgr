# -*- coding: utf-8 -*-
'''
Created on 2016年7月27日

@author: zqh
'''
import hashlib
import json
import os
import sys
import time
import traceback
import urllib
import urllib2
from datetime import datetime

TIMEFORMAT = '%Y-%m-%d %H:%M:%S.%f'


class ftlog():

    @staticmethod
    def formatStack(f=None, limit=None):
        return traceback.format_stack(f, limit)

    @staticmethod
    def formatExceptionLines(limit=None):
        try:
            etype, value, tb = sys.exc_info()
            return traceback.format_exception(etype, value, tb, limit)
        finally:
            etype = value = tb = None

    @staticmethod
    def _tostr(argl, argd):
        _log_msg = ""
        for l in argl:
            if type(l) == tuple:
                ps = str(l)
            else:
                try:
                    ps = "%r" % l
                except:
                    ps = str(l)
            if type(l) == str:
                _log_msg += ps[1:-1] + ' '
            elif type(l) == unicode:
                _log_msg += ps[2:-1] + ' '
            else:
                _log_msg += ps + ' '
        if len(argd) > 0:
            _log_msg += str(argd)
        return _log_msg

    @staticmethod
    def debug(*argl, **argd):
        print datetime.now().strftime(TIMEFORMAT), ftlog._tostr(argl, argd)

    @staticmethod
    def info(*argl, **argd):
        print datetime.now().strftime(TIMEFORMAT), ftlog._tostr(argl, argd)

    @staticmethod
    def error(*argl, **argd):
        ct = datetime.now().strftime(TIMEFORMAT)
        print ct, "************************************************************"
        print ct,   ftlog._tostr(argl, argd)
        lines = ftlog.formatExceptionLines()
        for l in lines:
            print ct, l[0:-1]
        print ct, "------------------------ Call Stack ------------------------"
        lines = ftlog.formatStack()
        for l in lines:
            print ct, l[0:-1]
        print ct, "************************************************************"

_DEBUG = 1

if not _DEBUG:
    @staticmethod
    def debug(*argl, **argd):
        pass
    ftlog.debug = debug


def md5digest(md5str):
    m = hashlib.md5()
    m.update(md5str)
    md5code = m.hexdigest()
    return md5code.lower()


def toHttpStr(data):
    if isinstance(data, (str, unicode)):
        data = urllib.quote(data)
    elif isinstance(data, dict):
        data = urllib.urlencode(data)
    elif isinstance(data, (list, tuple, int, float, bool)):
        data = urllib.quote(json.dumps(data))
    else:
        data = urllib.quote(str(data))
    return data


def doSyncQueryHttp(posturl, datadict=None):
    Headers = {'Content-type': 'application/x-www-form-urlencoded'}
    postData = None
    if datadict:
        postData = toHttpStr(datadict)
    request = urllib2.Request(url=posturl, data=postData, headers=Headers)
    response = urllib2.urlopen(request)
    if not response is None:
        retstr = response.read()
        return retstr
    return None


def syncDataFromGdss(dataType, apiName):
    httpgdss = os.environ.get('http_gdss', 'http://gdss.touch4.me')
    ftlog.info('GDSS->', httpgdss,  apiName, dataType)
    ct = int(time.time())
    sign = md5digest('gdss.touch4.me-api-' + str(ct) + '-gdss.touch4.me-api')
    posturl = '%s/?act=api.%s&time=%d&sign=%s' % (httpgdss, apiName, ct, sign)
    retstr = doSyncQueryHttp(posturl, {})
    datas = None
    try:
        datas = json.loads(retstr)
    except:
        pass
    if datas and isinstance(datas, dict):
        dictdata = datas.get('retmsg', None)
        if isinstance(dictdata, dataType) and len(dictdata) > 0:
            return dictdata
        else:
            ftlog.info('ERROR, _syncDataFromGdss, datas not found, datas=', datas)
    else:
        ftlog.info('ERROR, _syncDataFromGdss, gdss return error, datas=', datas)
    raise Exception('ERROR !! GDSS data get False ! Please Try Again !' + str(httpgdss) + ' ' + str(apiName))


def getGdssDatas():
    cids = syncDataFromGdss(dict, 'getClientIdDict')
    prodids = syncDataFromGdss(dict, 'getProductIdDict')
    bieventids = syncDataFromGdss(dict, 'getEventIdDict')
    return cids, prodids, bieventids


def convertBaseFile(basefile, runfile):
    # ftlog.info('convertBaseFile->', basefile, runfile)
    if basefile:
        return basefile
    if runfile.find('/_loader/game5_') >= 0:
        return runfile.replace('/_loader/game5_', '/game5/')
    if runfile.find('/_loader/poker5/') >= 0:
        return runfile.replace('/_loader/poker5/', '/poker5/')
    if runfile.find('/_loader/') >= 0:
        return runfile.replace('/_loader/', '/game5/')
    return runfile


def getPathInfo(basefile):
    '''
    获取当前文件所在配置模块的基本信息
    返回：tuple(
        9999,
        "/<proj>/game/9999/ads5",
        "/<proj>/game/%s/ads5",
        "game:9999:ads5:", 
        "game:%s:ads5:")
    '''
    if basefile.endswith('.py') or basefile.endswith('.pyc'):
        basefile = convertBaseFile(None, basefile)
    pdir = os.path.dirname(os.path.abspath(basefile))
    ppdir = os.path.dirname(pdir)
    pppdir = os.path.dirname(ppdir)
    key = os.path.basename(pppdir) + ':' + os.path.basename(ppdir) + ':' + os.path.basename(pdir) + ':'
    keyf = os.path.basename(pppdir) + ':%s:' + os.path.basename(pdir) + ':'
    pathf = pppdir + '/%s/' + os.path.basename(pdir)
    try:
        gameId = int(os.path.basename(ppdir))
    except:
        gameId = 0
    return gameId, pdir, pathf, key, keyf


def decodeObjUtf8(datas):
    '''
    遍历datas(list,dict), 将遇到的所有的字符串进行encode utf-8处理
    '''
    if isinstance(datas, dict):
        ndatas = {}
        for key, val in datas.iteritems():
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            ndatas[key] = decodeObjUtf8(val)
        return ndatas
    if isinstance(datas, list):
        ndatas = []
        for val in datas:
            ndatas.append(decodeObjUtf8(val))
        return ndatas
    if isinstance(datas, unicode):
        return datas.encode('utf-8')
    return datas


def writeJsonFile(fpath, datas, decodeUtf8=1):
    if decodeUtf8:
        datas = decodeObjUtf8(datas)
        datas = json.dumps(datas, indent=2, sort_keys=True, ensure_ascii=False)
    else:
        datas = json.dumps(datas, indent=2, sort_keys=True)
    fp = None
    try:
        fp = open(fpath, 'w+b')
        fp.write(datas)
    except:
        ftlog.error('The File JSON Format Error', fpath)
        raise
    finally:
        try:
            fp.close()
        except:
            pass


def readJsonFile(fpath, replaceEvn=1):
    if not os.path.isfile(fpath):
        # ftlog.info('The File JSON Not Found', fpath)
        return {}
    fp = None
    try:
        fp = open(fpath, 'r')
        sdata = fp.read()
        if replaceEvn:
            from _loader.mainconf import ENVS
            for k, v in ENVS.iteritems():
                sdata = sdata.replace(k, v)
        datas = json.loads(sdata)
        return datas
    except:
        ftlog.error('The File JSON Format Error', fpath)
        raise
    finally:
        try:
            fp.close()
        except:
            pass


def readJsonData(jpath, jfile, keycount, replaceEvn=1):
    if jpath:
        jfullpath = os.path.normpath(jpath + '/' + jfile)
    else:
        jfullpath = os.path.normpath(jfile)
    if not jfullpath.endswith('.json'):
        # 忽律非json文件
        return None, None
    if jfullpath.find('.svn') > 0:
        # 忽律非svn文件
        return None, None
    if jfullpath.find(os.path.sep + '.') > 0:
        # 忽律隐藏文件
        return None, None
    if os.path.isfile(jfullpath):
        rkey = ':'.join(jfullpath.split(os.path.sep)[-keycount:])
        rkey = rkey[0:-5]
        # ftlog.info('READ FILE ->', rkey, jfullpath)
        data = readJsonFile(jfullpath, replaceEvn)
        return rkey, data
    return None, None


def prepOutPut(cmlist, pyfile):
    _gameId, pdir, _pathf, _key, _keyf = getPathInfo(pyfile)
    pdir = os.path.dirname(os.path.dirname(pdir))
    # ftlog.info('UPGRADE OUT PATH->', pdir)
    for cm in cmlist:
        outpath = pdir + '/' + str(cm.gameId) + '/' + cm.module
        if not os.path.exists(outpath):
            os.makedirs(outpath)
        cm.outpath = outpath
