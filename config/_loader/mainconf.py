# -*- coding: utf-8 -*-
'''
Created on 2016年7月27日

@author: zqh
'''
from copy import deepcopy
import json
import os
import re

from _loader import mainhelper
from _loader.mainhelper import ftlog

GAMEIDS = []  # 所有配置目录下的gameid列表，按大小排序
ENVS = {}  # 配置系统提供的环境变量
CLIENTIDS = {}  # 全体CLIENTID的配置集合 str-int
CLIENTIDS_INT = {}  # 全体CLIENTID的配置集合 int-str
CLITNEIDS_INT_GAMEID = {}
CLITNEIDS_INT_SYS = {}
CLITNEIDS_INT_VER = {}
PRODUCTIDS = {}  # 全体PRODUCT的ID配置集合 str-int
PRODUCTIDS_INT = {}  # 全体PRODUCT的ID配置集合 int-str

BIEVENTIDS = {}
BIEVENTIDS_INT = {}

OUT_STATIC = {}
OUT_REDIS = {}

# 各种hall5大厅的游戏列表，避免大厅配置文件冲突
# modify by yzx at 2018年05月09日17:47:35
HALL_GAME_ID = [9999, 9998]

def init(basefile=None):
    if GAMEIDS:
        return

    def getGameIdFromHallClientId(clientId):
        try:
            gid = re.match('^.*-hall(\\d+).*$', clientId).group(1)
            return int(gid)
        except:
            # ftlog.info('WARRING clientId format error !' + str(clientId))
            return 0

    def getClientSys(clientId):
        clientsys = clientId[0]
        if clientsys == 'W' or clientsys == 'w':
            clientsys = 'winpc'
        elif clientsys == 'I' or clientsys == 'i':
            clientsys = 'ios'
        elif clientsys == 'H' or clientsys == 'h':
            clientsys = 'h5'
        elif clientsys == 'M' or clientsys == 'm':
            clientsys = 'mac'
        else:
            clientsys = 'android'
        return clientsys

    def _getClientVer(clientId):
        infos = clientId.split('_', 2)
        ver = float(infos[1])
        return ver

    global CLIENTIDS, PRODUCTIDS, BIEVENTIDS
    CLIENTIDS,  PRODUCTIDS, BIEVENTIDS = mainhelper.getGdssDatas()
    for k, v in PRODUCTIDS.iteritems():
        PRODUCTIDS_INT[str(v)] = k
    for k, v in BIEVENTIDS.iteritems():
        BIEVENTIDS_INT[str(v)] = k

    for k, v in CLIENTIDS.iteritems():
        v = str(v)
        CLIENTIDS_INT[v] = k
        CLITNEIDS_INT_GAMEID[v] = getGameIdFromHallClientId(k)
        CLITNEIDS_INT_SYS[v] = getClientSys(k)
        CLITNEIDS_INT_VER[v] = _getClientVer(k)

    basefile = mainhelper.convertBaseFile(basefile, __file__)
    pdir = os.path.dirname(os.path.abspath(basefile))
    ftlog.info('CONFIGURE PATH:', pdir)
    for gds in os.listdir(pdir):
        if gds[0] == '.':
            continue
        try:
            GAMEIDS.append(int(gds))
        except:
            continue
    GAMEIDS.sort()
#     if 9998 in GAMEIDS:
#         GAMEIDS.remove(9998)
#     if 9995 in GAMEIDS:
#         GAMEIDS.remove(9995)
#     if 9996 in GAMEIDS:
#         GAMEIDS.remove(9996)
    ftlog.info('CONFIGURE GAMEIDS:', GAMEIDS)

    http_download = os.environ.get('http_download')
    if not http_download:
        http_download = 'http://ddz.dl.tuyoo.com/cdn5'
    http_game = os.environ.get('http_game')
    if not http_game:
        http_game = 'http://open.touch4.me'

    ENVS['${http_download}'] = http_download
    ENVS['${http_game}'] = http_game


class TcVcModule(object):

    def __init__(self, gameId, baseKey, vcDatas, tcDatas, scDatas):
        self.gameId = gameId
        self.baseKey = baseKey
        self.vcKey = baseKey + 'vc'
        self.tcKey = baseKey + 'tc'
        self.scKey = baseKey + 'sc'
        self.module = baseKey.split(':')[-2]
        self.vcDatas = vcDatas
        self.tcDatas = tcDatas
        self.scDatas = scDatas
        self.outpath = ''  # 输出的文件路径

    def __str__(self):
        return 'TcVcModule: baseKey=' + str(self.baseKey) + \
            ' vcDatas=' + json.dumps(self.vcDatas) + ' tcDatas=' + json.dumps(self.tcDatas) +\
            ' scDatas=' + json.dumps(self.scDatas)

    def __repr__(self):
        return str(self)

    def writeOut(self, fileName, datas):
        mainhelper.writeJsonFile(self.outpath + '/' + fileName, datas)


class JsonDataModule(object):

    def __init__(self, gameId, baseKey):
        self.gameId = gameId
        self.baseKey = baseKey
        self.module = baseKey.split(':')[-2]
        self.datas = {}
        self.outpath = ''  # 输出的文件路径

    def __str__(self):
        return 'JsonDataModule: gameId=' + str(self.gameId) + ' baseKey=' + str(self.baseKey) + \
            ' datas=' + json.dumps(self.datas)

    def __repr__(self):
        return str(self)

    def writeOut(self, fileName, datas):
        mainhelper.writeJsonFile(self.outpath + '/' + fileName, datas)


def getGameDatas(basefile, replaceEvn=1):
    '''
    读取当前游戏下的对应的所有的json的数据信息
    返回 TcVcModule实例
    '''
    gameId, pdir, _pathf, key, _keyf = mainhelper.getPathInfo(basefile)
    ftlog.info('READ GAME', pdir)
    jdata = JsonDataModule(gameId, key)
    sfs = os.listdir(pdir)
    for f in sfs:
        rkey, datas = mainhelper.readJsonData(pdir, f, 1, replaceEvn)
        if rkey:
            jdata.datas[rkey] = datas
    return jdata


def getGameDatas0All(basefile, replaceEvn=1):
    '''
    读取当所有游戏下同名的配置模块下的所有的tc的数据信息
    返回 TcVcModule实例的集合
    '''
    cmlist = []
    _gameId, _pdir, pathf, _key, _keyf = mainhelper.getPathInfo(basefile)
    if _gameId in HALL_GAME_ID:
        HALL_GAME_ID.remove(_gameId)
    ftlog.info('READ ALL', pathf, _gameId, HALL_GAME_ID)
    for gid in GAMEIDS:
        if gid in HALL_GAME_ID:
            ftlog.info("current:", _gameId," skip: ", gid)
            continue
        fpath = pathf % (gid)
        rkey, datas = mainhelper.readJsonData('', fpath + '/0.json', 1, replaceEvn)
        if rkey and datas:
            jdata = JsonDataModule(gid, _keyf % (gid))
            jdata.datas[rkey] = datas
            cmlist.append(jdata)
    return cmlist


def getTcVcDatasGame(basefile, replaceEvn=1):
    '''
    读取当前游戏下的对应的vc、tc的数据信息
    返回 TcVcModule实例
    '''
    gameId, pdir, _pathf, key, _keyf = mainhelper.getPathInfo(basefile)
    ftlog.info('READ GAME', pdir)
    tc = mainhelper.readJsonFile(pdir + '/tc.json', replaceEvn)
    vc = mainhelper.readJsonFile(pdir + '/vc.json', replaceEvn)
    sc = mainhelper.readJsonFile(pdir + '/sc.json', replaceEvn)
    cm = TcVcModule(gameId, key, vc, tc, sc)
    return cm


def getTcVcScDatasAll(basefile, replaceEvn=1):
    '''
    读取当所有游戏下同名的配置模块下的所有的vc、tc、sc的数据信息
    返回 TcVcModule实例的集合
    '''
    cmlist = []
    _gameId, _pdir, pathf, _key, _keyf = mainhelper.getPathInfo(basefile)
    if _gameId in HALL_GAME_ID:
        HALL_GAME_ID.remove(_gameId)
    ftlog.info('READ ALL', pathf, _gameId, HALL_GAME_ID)
    for gid in GAMEIDS:
        if gid in HALL_GAME_ID:
            ftlog.info("current:", _gameId," skip: ", gid)
            continue
        fpath = pathf % (gid)
        ftlog.info('READ GAME', fpath)
        tc = mainhelper.readJsonFile(fpath + '/tc.json', replaceEvn)
        vc = mainhelper.readJsonFile(fpath + '/vc.json', replaceEvn)
        sc = mainhelper.readJsonFile(fpath + '/sc.json', replaceEvn)
        cm = TcVcModule(gid, _keyf % (gid),  vc, tc, sc)
        cmlist.append(cm)
    return cmlist


def getTcDatasAll(basefile, replaceEvn=1):
    '''
    读取当所有游戏下同名的配置模块下的所有的tc的数据信息
    返回 TcVcModule实例的集合
    '''
    cmlist = []
    _gameId, _pdir, pathf, _key, _keyf = mainhelper.getPathInfo(basefile)
    ftlog.info('READ ALL', pathf)
    if _gameId in HALL_GAME_ID:
        HALL_GAME_ID.remove(_gameId)
    ftlog.info('READ ALL', pathf, _gameId, HALL_GAME_ID)
    for gid in GAMEIDS:
        if gid in HALL_GAME_ID:
            ftlog.info("current:", _gameId, " skip: ", gid)
            continue
        fpath = pathf % (gid)
        ftlog.info('READ GAME', fpath)
        tc = mainhelper.readJsonFile(fpath + '/tc.json', replaceEvn)
        cm = TcVcModule(gid, _keyf % (gid),  None, tc, None)
        cmlist.append(cm)
    return cmlist


def meargeCmModules(cmlist, targetGameId=9999):  # 当有gameid大于9999时会冲掉9999的配置
    '''
    合并cmlist中的所有的TcVcModule的vcDatas和tcDatas到一个新的TcVcModule
    返回：合并后的TcVcModule实例, 其tcKey和vcKey使用cmlist[-1]对象的值 或 使用targetGameId对应的值
    '''
    vdatas = {}
    tdatas = {}
    sdatas = {}
    cm9999 = None
    for cm in cmlist:
        if cm.tcDatas:
            for k, v in cm.tcDatas.iteritems():
                if not k in tdatas:
                    tdatas[k] = deepcopy(v)
                else:
                    if isinstance(v, dict):
                        tdatas[k].update(deepcopy(v))
                    elif isinstance(v, list):
                        tdatas[k].extend(deepcopy(v))
                    else:
                        tdatas[k] = deepcopy(v)

        if cm.scDatas:
            for k, v in cm.scDatas.iteritems():
                if not k in sdatas:
                    sdatas[k] = deepcopy(v)
                else:
                    if isinstance(v, dict):
                        sdatas[k].update(deepcopy(v))
                    elif isinstance(v, list):
                        sdatas[k].extend(deepcopy(v))
                    else:
                        sdatas[k] = deepcopy(v)

        if cm.vcDatas:
            vdatas.update(deepcopy(cm.vcDatas))

        if cm.gameId == targetGameId:
            cm9999 = cm
    if not cm9999:
        cm9999 = cmlist[-1]
    cm = TcVcModule(cm9999.gameId, cm9999.baseKey, vdatas, tdatas, sdatas)
    return cm


def exportStatic(key, basefile, datas):
    gameId, _, _, _, _ = mainhelper.getPathInfo(basefile)
    key = 'game5:%s:%s:gcsc' % (str(gameId), key)
    OUT_STATIC[key] = deepcopy(datas)
    ftlog.debug('OUT_STATIC', key, json.dumps(datas))


def exportRedis(key, datas):
    OUT_REDIS[key] = deepcopy(datas)
    ftlog.debug('OUT_REDIS', key, json.dumps(datas))


def upgradeTemplatesValueList(cmlist):
    for cm in cmlist:
        if 'templates' not in cm.tcDatas:
            cm.tcDatas['templates'] = {}
        templates = cm.tcDatas['templates']
        for k in templates.iterkeys():
            v = templates[k]
            if v:
                if isinstance(v, list) and len(v) == 1:
                    templates[k] = v[0]
            else:
                del templates[k]


# def upgradeTemplatesRef(cmlist):
#     actuals = {}
#     cmgids = {}
#     defaults = {}
#     for cm in cmlist:
#         tid = 1
#         if 'templates' not in cm.tcDatas:
#             cm.tcDatas['templates'] = {}
#         templates = cm.tcDatas['templates']
#
#         if isinstance(templates, list):
#             ntemps = {}
#             for t in templates:
#                 ntemps[t['name']] = t
#             cm.tcDatas['templates'] = ntemps
#             templates = ntemps
#
#         for k, t in templates.iteritems():
#             if 'name' not in t:
#                 t['name'] = k
#             t['id'] = cm.gameId * 1000000 + tid
#             tid += 1
#
#         cmgids[cm.gameId] = cm
#         actuals.update(cm.vcDatas.get('actual', {}))
#         defaults[cm.gameId] = {}
#         for k, v in cm.vcDatas.iteritems():
#             defaults[cm.gameId][k] = v
#         cm.vcDatas = {}
#
#     ciall = set(CLIENTIDS_INT.keys())
#     for ci in ciall:
#         gid = CLITNEIDS_INT_GAMEID[ci]
#         cm = cmgids.get(gid)
#         if cm:
#             templates = cm.tcDatas['templates']
#             tname = actuals.get(ci)
#             if tname:
#                 if tname in templates:
#                     cm.vcDatas[ci] = templates[tname]['id']
#                     ftlog.info('find 1:1 template of', ci, cm.vcDatas[ci])
#                 else:
#                     ftlog.info('WARRING ! not found template !', ci, CLITNEIDS_INT_GAMEID[ci], CLIENTIDS_INT[ci])
#             else:
#                 # 获取缺省设置
#                 dci = 'default_' + CLITNEIDS_INT_SYS[ci]
#                 if dci in defaults[gid]:
#                     # 使用缺省系统的模板
#                     tname = defaults[gid][dci]
#                     if tname in templates:
#                         cm.vcDatas[ci] = templates[tname]['id']
#                         ftlog.info('find default os template of', ci, cm.vcDatas[ci])
#                     else:
#                         ftlog.info('WARRING ! not found template !', ci, CLITNEIDS_INT_GAMEID[ci], CLIENTIDS_INT[ci])
#                 elif 'default' in defaults[gid]:
#                     # 使用缺省系统的模板
#                     tname = defaults[gid]['default']
#                     if tname in templates:
#                         cm.vcDatas[ci] = templates[tname]['id']
#                         ftlog.info('find default template of', ci, cm.vcDatas[ci])
#                     else:
#                         ftlog.info('WARRING ! not found template !', ci, CLITNEIDS_INT_GAMEID[ci], CLIENTIDS_INT[ci])
#                 else:
#                     # 没有找到任何模板
#                     ftlog.info('WARRING ! not found template !', ci, CLITNEIDS_INT_GAMEID[ci], CLIENTIDS_INT[ci])
#         else:
#             ftlog.info('WARRING !! not found template !', ci, CLITNEIDS_INT_GAMEID[ci], CLIENTIDS_INT[ci])
#
#     for cm in cmlist:
#         cm.tcDatas['templates'] = cm.tcDatas['templates'].values()


def upgradeTemplatesRef(cmlist, templateIdPrefix, defaultTemplate='default'):
    for cm in cmlist:
        if 'templates' not in cm.tcDatas:
            cm.tcDatas['templates'] = {}
        if 'actual' not in cm.vcDatas:
            cm.vcDatas['actual'] = {}
        if 'default' not in cm.vcDatas:
            cm.vcDatas['default'] = defaultTemplate

        if isinstance(cm.tcDatas['templates'], list):
            ntemps = {}
            for t in cm.tcDatas['templates']:
                ntemps[t['name']] = t
            cm.tcDatas['templates'] = ntemps

        # 补丁，有些模板使用的key和name值不一致
        for k, v in cm.tcDatas['templates'].iteritems():
            v['name'] = k

    if len(cmlist) > 1:  # 把9999模板复制到各游戏
        templates9999 = None
        for cm in cmlist:
            if cm.gameId == 9999:
                templates9999 = cm.tcDatas['templates']
                break
        if templates9999:
            for cm in cmlist:
                templates = cm.tcDatas['templates']
                templates.update(deepcopy(templates9999))

    actuals = {}  # 1：1的模板对应表 clientId <-> templateName
    cmgids = {}  # gameId对应的cm对象  gameId <-> TcVcModule
    defaults = {}  # 缺省的模板对应 gameId <-> { "deftult" : "templateName"}
    for cm in cmlist:
        actuals.update(cm.vcDatas['actual'])
        defaults[cm.gameId] = {}
        for k, v in cm.vcDatas.iteritems():
            if k != 'actual':
                defaults[cm.gameId][k] = v
        cm.vcDatas = {}
        cmgids[cm.gameId] = cm

    # 检查、更新clientId<->模板名称的对应关系
    errCount = 0
    isHall = False
    if len(cmgids) == 1 and cmgids.keys()[0] == 9999:  # 这种是大厅独有配置,所有clientid都配置到大厅
        isHall = True
    ciall = set(CLIENTIDS_INT.keys())
    for ci in ciall:
        gid = 9999 if isHall else CLITNEIDS_INT_GAMEID[ci]  # 否则clientid配置到各游戏
        cm = cmgids.get(gid)
        if cm:
            templates = cm.tcDatas['templates']
            tnameActual = actuals.get(ci)
            if tnameActual and tnameActual not in templates:
                ftlog.info('MATCH ERROR 1, template name not Found [', tnameActual, '], gameId=', gid, 'clinetId=', ci, CLIENTIDS_INT[ci])
                tnameActual = None
                errCount += 1

            # 使用缺省系统的模板
            tnameDefaultOs = defaults[gid].get('default_' + CLITNEIDS_INT_SYS[ci])
            if tnameDefaultOs and tnameDefaultOs not in templates:
                ftlog.info('MATCH ERROR 2, template name not Found [', tnameDefaultOs, '], gameId=', gid, 'clinetId=', ci, CLIENTIDS_INT[ci])
                tnameDefaultOs = None
                errCount += 1

            # 使用缺省系统的模板
            tnameDefault = defaults[gid].get('default')
            if tnameDefault and tnameDefault not in templates:
                ftlog.info('MATCH ERROR 3, template name not Found [', tnameDefault, '], gameId=', gid, 'clinetId=', ci, CLIENTIDS_INT[ci])
                tnameDefault = None
                errCount += 1

            if tnameActual:
                cm.vcDatas[ci] = tnameActual
                # ftlog.info('MATCH ACTUAL, gameId=', gid, 'clinetId=', ci, 'template=', tnameActual)
            elif tnameDefaultOs:
                cm.vcDatas[ci] = tnameDefaultOs
                # ftlog.info('MATCH DEFAULT 1, gameId=', gid, 'clinetId=', ci, 'template=', tnameDefaultOs)
            elif tnameDefault:
                cm.vcDatas[ci] = tnameDefault
                # ftlog.info('MATCH DEFAULT 2, gameId=', gid, 'clinetId=', ci, 'template=', tnameDefault)
            else:
                ftlog.info('MATCH ERROR 4, gameId=', gid, 'clinetId=', ci, CLIENTIDS_INT[ci])
                errCount += 1
        else:
            ftlog.info('MATCH ERROR 5, template name not Found [ None ], gameId=', gid, 'clinetId=', ci, CLIENTIDS_INT[ci])
            errCount += 1
    # 删除无效的模板
    for cm in cmlist:
        usedTemplate = set(cm.vcDatas.values())
        for k in cm.tcDatas['templates'].keys():
            if k not in usedTemplate:
                ftlog.info('DELETE UNUSED TEMPLATE:', cm.gameId, k)
                del cm.tcDatas['templates'][k]
    # 模板恢复LIST数据格式
    for cm in cmlist:
        cm.tcDatas['templates'] = cm.tcDatas['templates'].values()
        cm.tcDatas['templates'].sort(key=lambda x: x['name'])

    # 调整模板的name至id，统一化, id为唯一标识，引用标识
    for cm in cmlist:
        for t in cm.tcDatas['templates']:
            t['id'] = t['name']
            del t['name']

    ftlog.info('TOTAL CLINETID COUNT=%s, ERROR COUNT=%s, OK PERCENT %0.2f' % (len(CLIENTIDS_INT), errCount, (100 - 100.0 * errCount / len(CLIENTIDS_INT))))
    from _loader.updateref import AutoModuleId
    for cm in cmlist:
        newTemplateId = AutoModuleId(templateIdPrefix, cm.gameId)
        # 转换模板的ID和引用的ID
        for template in cm.tcDatas['templates']:
            template['id'] = newTemplateId.newId(template['id'])
        # 转换clientId和模板的对应ID
        for cid in cm.vcDatas.iterkeys():
            tid = cm.vcDatas[cid]
            cm.vcDatas[cid] = newTemplateId.newId(tid)


def transformList2Dict(listDatas, idName='id'):
    dictData = {}
    for tt in listDatas:
        tid = tt[idName]
        dictData[tid] = tt
        del tt[idName]
    return dictData
