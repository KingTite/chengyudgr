# -*- coding: utf8 -*-


from freetime5.util import ftlog
from tuyoo5.core.tyconfig import TyCachedConfig
from tuyoo5.core import tyglobal


def CheckMD5ReturnNewconfig(clientMd5Dict):
    '''
    检查最新的md5，并传最新的配置给客户端
    客户端参数，服务器配置
    {
        'advance':md5
    }
    :return:
     {
        'advance':{'md5':'', }
    }
    '''
    gameId = tyglobal.gameId()
    scconf = TyCachedConfig('md5', tyglobal.gameId()).getScConfig()
    retdict = {}
    for key, val in clientMd5Dict.items():
        if key in ['userId', 'clientId', 'cloudId', 'version']:
            continue
        ftlog.debug('CheckMD5ReturnNewconfig scconf ->', scconf)
        newmd5 = scconf[key]
        if newmd5 != val:
            retdict[key] = {
                'md5': newmd5,
                'conf': TyCachedConfig(key, gameId).getScConfig()
            }
    if ftlog.is_debug():
        ftlog.debug('CheckMD5ReturnNewconfig',
                    'gameId = ', gameId,
                    'retdict = ', retdict
                    )
    mo = {}
    mo['code'] = 0
    mo['data'] = retdict
    return mo
