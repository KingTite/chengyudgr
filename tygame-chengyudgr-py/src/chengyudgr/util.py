# -*- coding: utf8 -*-

from tuyoo5.core import tyglobal
from tuyoo5.core import tyrpcsdk, tyrpchall
from freetime5.util import ftlog
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

ERROR_USER_ID = -1
_DEBUG, debug = ftlog.getDebugControl(__name__)

def getClientId():
    return 'Android_5.0_tyGuest,wechat.alipay,wechat.0-hall20312.tu.chengydgr'

def isIosUser(clientId):
    """
    是否是ios
    @param clientId:
    @return:
    """
    ios = 'IOS_1.0_tyGuest,facebook.appStore.0-hall20220.appStore.chengyudgr'
    if clientId == ios:
        return True
    return False

def isAndroidUser(clientId):
    """
    是否是Android
    @param clientId:
    @return:
    """
    android_clientId = 'Android_5.0_tyGuest,wechat.alipay,wechat.0-hall20312.tu.chengydgr'
    if clientId == android_clientId:
        return True
    return False

def getDomain():
    '''获取域名'''
    if tyglobal.mode() == tyglobal.RUN_MODE_ONLINE:
        url = 'http://ptceshi.touch4.me'
    else:
        url = 'http://opencx.nalrer.cn'
    return url


def IsExist(userId):
    '''
    判断用户是否存在
    :param userId:
    :return:
    '''
    try:
        if userId <= 0:
            return False
        userInfo = tyrpcsdk.getUserDatas(userId, tyrpchall.UserKeys.ATT_CREATE_TIME)
        if userInfo and userInfo.get('createTime'):
            return True
    except:
        return False
    return False


# 如果text不足16位的倍数就用空格补足为16位
def add_to_16(text):
    if len(text.encode('utf-8')) % 16:
        add = 16 - (len(text.encode('utf-8')) % 16)
    else:
        add = 0
    text = text + ('\0' * add)
    return text.encode('utf-8')

