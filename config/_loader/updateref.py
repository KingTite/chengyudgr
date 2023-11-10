# -*- coding: utf-8 -*-
'''
Created on 2016年7月27日

@author: zqh
'''

from copy import deepcopy
import json
import os

from _loader import mainhelper
from _loader.mainhelper import ftlog


class AutoModuleId(object):
    def __init__(self, moduleName, gameId):
        self.moduleName = moduleName
        self.gameId = gameId
        self.idNum = 0
        self.oldNewMap = {}
        self.newIds = set()

    def newId(self, oldId):
        if oldId in self.oldNewMap:
            return self.oldNewMap[oldId]
        self.idNum += 1
        newId = '%s:%s:%s' % (self.moduleName, self.gameId, self.idNum)
        self.oldNewMap[oldId] = newId
        self.newIds.add(newId)
        return newId


class AutoModuleIdAll(object):
    """
    注意：生成模板id的时候，不要用这个类；
    因为hall37里边模板是跨游戏使用的(起码大厅的模板是公用的),
    使用这个类,假设game6使用了game3的模板,game6会得到module:3:num这种id,这不是想要的

    要保证不混用,比如活动id,可以使用此类
    """

    def __init__(self, moduleName):
        self.moduleName = moduleName
        self.idNums = {}
        self.oldNewMap = {}
        self.newIds = set()

    def newId(self, gameId, oldId):
        if oldId in self.oldNewMap:
            return self.oldNewMap[oldId]
        if gameId not in self.idNums:
            self.idNums[gameId] = 0
        self.idNums[gameId] += 1
        newId = '%s:%s:%s' % (self.moduleName, gameId, self.idNums[gameId])
        self.oldNewMap[oldId] = newId
        self.newIds.add(newId)
        return newId

    def getNewId(self, oldId):
        return self.oldNewMap[oldId]


class UpdateRef(object):
    def __init__(self, modulename, basefile):
        self._TODOMAP = None
        self._TODOMAP_REV = None
        self._TODOIDS = None
        self.basefile = basefile
        self.modulename = modulename

    def getDefDictStr(self, defDict):
        defDict = deepcopy(defDict)
        if 'id' in defDict:
            del defDict['id']
        if 'name' in defDict:
            del defDict['name']
        if 'ref' in defDict:
            del defDict['ref']
        return json.dumps(defDict, sort_keys=True)

    def upgradeInit(self):
        if self._TODOMAP is not None:
            return
        from _loader import mainconf
        cmlist = mainconf.getTcDatasAll(self.basefile, 0)
        self._TODOMAP = {}
        self._TODOMAP_REV = {}
        self._TODOIDS = {}
        for cm in cmlist:
            for tt in cm.tcDatas.get('templates', []):
                print tt
                gameId = int(cm.gameId)
                tt['__gameId'] = gameId
                tid = tt['id']
                self._TODOMAP[tid] = tt
                try:
                    self._TODOIDS[gameId] = max(self._TODOIDS.get(gameId, 0), int(tid.split(':')[-1]))
                except:
                    if gameId not in self._TODOIDS:
                        self._TODOIDS[gameId] = 0

                self._TODOMAP_REV[self.getDefDictStr(tt)] = tid
                print 'upgradeInit->', self.modulename, self._TODOIDS

    def getUpgradeId(self, gameId, tododef):
        self.upgradeInit()
        gameId = int(gameId)
        tododef['__gameId'] = gameId
        tododefstr = self.getDefDictStr(tododef)
        tid = self._TODOMAP_REV.get(tododefstr, 0)
        if not tid:
            if gameId not in self._TODOIDS:
                self._TODOIDS[gameId] = 0
            self._TODOIDS[gameId] += 1
            tid = '%s:%s:%s' % (self.modulename, gameId, self._TODOIDS[gameId])
            self._TODOMAP_REV[tododefstr] = tid
            self._TODOMAP[tid] = deepcopy(tododef)
            self._TODOMAP[tid]['id'] = tid
        return tid

    def svaeUpgrade(self, writeJson=True):
        self.upgradeInit()

        todos = self._TODOMAP.values()
        gtodos = {}
        for t in todos:
            gid = t['__gameId']
            if gid in gtodos:
                gtodos[gid].append(t)
            else:
                gtodos[gid] = [t]
            del t['__gameId']

        if writeJson:
            _gameId, pdir, _pathf, _key, _keyf = mainhelper.getPathInfo(self.basefile)
            pdir = os.path.dirname(os.path.dirname(pdir))
            ftlog.info('UPGRADE OUT PATH->', pdir, self.modulename)
            for gid, tlist in gtodos.iteritems():
                outpath = pdir + '/' + str(gid) + '/' + self.modulename
                if not os.path.exists(outpath):
                    os.makedirs(outpath)
                datas = {'templates': tlist}
                mainhelper.writeJsonFile(outpath + '/tc.json', datas)

            self._TODOMAP = None
            self._TODOMAP_REV = None
            self._TODOIDS = None


class UpdateRefSingle(UpdateRef):
    def __init__(self, module):
        super(UpdateRefSingle, self).__init__(module, '')
        self.upgradeInit()

    def upgradeInit(self):
        if self._TODOMAP is not None:
            return
        self._TODOMAP = {}
        self._TODOMAP_REV = {}
        self._TODOIDS = {}
