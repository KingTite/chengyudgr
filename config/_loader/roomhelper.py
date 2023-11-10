# -*- coding: utf-8 -*-
'''
Created on 2016年7月29日

@author: zqh
'''
import json

from _loader import mainconf


def loadRooms(basefile, funRoomConfCheck):
    jdata = mainconf.getGameDatas(basefile)
    bigRoomIds = set([])
    for rdef in jdata.datas['0']:
        if 'bigRoomId' in rdef:
            bigRoomId = rdef['bigRoomId']
            rgid = int(bigRoomId / 1000)
            assert(rgid == jdata.gameId), 'the bigRoomId must start with gameid !' + str(jdata.gameId) + ' room=' + json.dumps(rdef)
            if bigRoomId in bigRoomIds:
                raise Exception('the bigRoomId already defined !' + str(bigRoomId) + ' ' + json.dumps(rdef))
            else:
                bigRoomIds.add(bigRoomId)
        else:
            bigRoomIdStart = rdef['bigRoomIdStart']
            bigRoomIdStop = rdef['bigRoomIdStop']
            rgid = int(bigRoomIdStart / 1000)
            assert(rgid == jdata.gameId), 'the bigRoomIdStart must start with gameid !' + str(jdata.gameId) + ' room=' + json.dumps(rdef)
            rgid = int(bigRoomIdStop / 1000)
            assert(rgid == jdata.gameId), 'the bigRoomIdStop must start with gameid !' + str(jdata.gameId) + ' room=' + json.dumps(rdef)
            assert(bigRoomIdStart < bigRoomIdStop), 'the bigRoomIdStart must little than bigRoomIdStop !' + str(jdata.gameId) + ' room=' + json.dumps(rdef)
            for bigRoomId in xrange(bigRoomIdStart, bigRoomIdStop + 1):
                if bigRoomId in bigRoomIds:
                    raise Exception('the bigRoomId already defined !' + str(bigRoomId) + ' ' + json.dumps(rdef))
                else:
                    bigRoomIds.add(bigRoomId)
    bigRoomIds = list(bigRoomIds)
    bigRoomIds.sort()
    for bigRoomId in bigRoomIds:
        rconf = jdata.datas.get(str(bigRoomId), None)
        if rconf is None:
            raise Exception('the room configure not found !' + str(jdata.gameId) + ' ' + str(bigRoomId))
        if funRoomConfCheck:
            funRoomConfCheck(jdata, bigRoomId, rconf)

    for bigRoomId in bigRoomIds:
        rconf = jdata.datas.get(str(bigRoomId), None)
        rkey = jdata.baseKey + str(bigRoomId)
        mainconf.exportRedis(rkey, rconf)
