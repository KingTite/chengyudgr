# -*- coding=utf-8 -*-
from freetime5.util import ftstr, ftlog
from chengyudgr import aes

def getParams(msg):
    body = msg.getBody()
    params = ftstr.loads(body, ignoreException=True, execptionValue={})

    if ftlog.is_debug():
        ftlog.debug('getParams',
                    'params=', params)
    # 解密数据
    params = get_param_data(params['secret'])
    return params

def get_param_data(secret):
    data = {}
    try:
        data = aes.decrypt(secret)
        data = ftstr.loads(data, ignoreException=True, execptionValue={})
        if ftlog.is_debug():
            ftlog.debug('get_param_data data->', data, type(data))
    except:
        return data
    return data

def check_userId(msg, _result, name):
    params = getParams(msg)
    try:
        val = int(params.get(name, 0))
        if val > 0:
            return val, None
    except:
        return None, 'the %s must large than zero !' % name

def check_clientId(msg, _result, name):
    params = getParams(msg)
    val = params.get(name, '').strip()
    if len(val) > 0:
        return val, None
    return None, 'the %s can not empty !' % (name)

def check_version(msg, _result, name):
    params = getParams(msg)
    val = params.get(name, '').strip()
    if len(val) > 0:
        return val, None
    return None, 'the %s can not empty !' % (name)

def check_base_geme_data(msg, _result, name):
    params = getParams(msg)
    val = params.get(name, {})
    if val:
        return val, None
    return None, 'the %s can not empty !' % (name)


def check_comment(msg, _result, name):
    params = getParams(msg)
    val = params.get(name, '').strip()
    if len(val) > 0:
        return val, None
    return None, 'the %s can not empty !' % (name)

def check_state(msg, _result, name):
    params = getParams(msg)
    val = params.get(name)
    if val is None:
        return None, 'the %s can not empty !' % (name)
    return val, None

def check_flower(msg, _result, name):
    params = getParams(msg)
    val = params.get(name)
    if val is None:
        return None, 'the %s can not empty !' % (name)
    return val, None

def check_rankName(msg, _result, name):
    params = getParams(msg)
    val = params.get(name, '').strip()
    if len(val) > 0:
        return val, None
    return None, 'the %s can not empty !' % (name)

def check_name(msg, _result, name):
    params = getParams(msg)
    val = params.get(name, '').strip()
    if len(val) > 0:
        return val, None
    return None, 'the %s can not empty !' % (name)


def check_icon(msg, _result, name):
    params = getParams(msg)
    val = params.get(name, '').strip()
    if len(val) > 0:
        return val, None
    return None, 'the %s can not empty !' % (name)

def check_kejvData(msg, _result, name):
    params = getParams(msg)
    val = params.get(name, {})
    if val:
        return val, None
    return None, 'the %s can not empty !' % (name)

def check_hardData(msg, _result, name):
    params = getParams(msg)
    val = params.get(name, {})
    if val:
        return val, None
    return None, 'the %s can not empty !' % (name)

def check_allTime(msg, _result, name):
    params = getParams(msg)
    val = params.get(name, 0)
    return val, None

def check_orderId(msg, _result, name):
    params = getParams(msg)
    val = params.get(name, '').strip()
    if len(val) > 0:
        return val, None
    return None, 'the %s can not empty !' % (name)

def check_prodId(msg, _result, name):
    params = getParams(msg)
    val = params.get(name, '').strip()
    if len(val) > 0:
        return val, None
    return None, 'the %s can not empty !' % (name)

def check_prodPrice(msg, _result, name):
    params = getParams(msg)
    val = params.get(name, 0)
    if val > 0:
        return val, None
    return None, 'the %s can not empty !' % (name)

def check_prodCount(msg, _result, name):
    params = getParams(msg)
    val = params.get(name, 0)
    if val > 0:
        return val, None
    return None, 'the %s can not empty !' % (name)

def check_questionId(msg, _result, name):
    params = getParams(msg)
    val = params.get(name, 0)
    if val > 0:
        return val, None
    return None, 'the %s can not empty !' % (name)

def check_dataKey(msg, _result, name):
    params = getParams(msg)
    val = params.get(name, '')
    if val:
        return val, None
    return None, 'the %s can not empty !' % (name)

def check_dataVal(msg, _result, name):
    params = getParams(msg)
    val = params.get(name)
    if not(val is None):
        return val, None
    return None, 'the %s can not empty !' % (name)

def check_isItem(msg, _result, name):
    params = getParams(msg)
    val = params.get(name)
    if not (val is None):
        return val, None
    return None, 'the %s can not empty !' % (name)

def check_shopVersion(msg, _result, name):
    params = getParams(msg)
    val = params.get(name, "shop1")
    return val, None

def check_collectList(msg, _result, name):
    params = getParams(msg)
    val = params.get(name)
    if not val:
        return None, 'the %s can not empty !' % (name)
    if not isinstance(val, list):
        return None, 'the %s can not list !' % (name)
    return val, None
