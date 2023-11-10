# -*- coding: utf-8 -*-

import json
import time
import hashlib
from freetime5.twisted import fthttp, ftcore
from freetime5.util import ftlog, ftstr, fttime
from tuyoo5.core import tyglobal
from tuyoo5.core.tyconfig import TyCachedConfig
from tuyoo5.game import tybireport
from chengyudgr.entity.dao import mixDaoGameData, DaoWordContact
from chengyudgr import util
import random
import requests


APPID = 'wxb7d07c42475bca95'
SECRET = '18dd0be17ade30c8ffe3ee5a913df444'

def get_wx_access_token_online():
    """
    获取线上token,保证一个中控机
    @return:
    """
    url = 'http://opencx.nalrer.cn/api/chengyudgr/get_wx_access_token'
    token = fthttp.queryHttp('GET', url, None, None, 5)
    ftlog.debug('_wx get_wx_access_token_online', token)
    if isinstance(token, str):
        return token
    if isinstance(token, tuple):
        return token[1]
    return None

def get_token_from_wx_server():
    """
    从微信服务器获取token
    @return:
    """
    ftlog.info('_wx get_token_from_wx_server in')
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (APPID, SECRET)
    _code, page = fthttp.queryHttp('GET', url, None, None, 5)
    new_token = ftstr.loads(page, ignoreException=True, execptionValue={})
    if not new_token.get('access_token', ''):
        raise Exception('_wx get_token_from_wx_server error!')
    new_token['timestamp'] = time.time()
    mixDaoGameData.set_wx_access_token(new_token)
    ftlog.info('_wx get_token_from_wx_server out ->', new_token)
    return new_token

def get_wx_access_token():
    """
    获取token
    """
    # 是否需要重新获取
    is_get_new_token = True
    # 获取数据库的token
    db_token = mixDaoGameData.get_wx_access_token()
    # token是否过期或者数据库不存在
    if db_token and (int(time.time()) - int(db_token['timestamp'])) < db_token['expires_in']:
        is_get_new_token = False
    # 重新获取token
    if not is_get_new_token:
        result = db_token['access_token']
    else:
        # 测试服和正式服做区分
        if tyglobal.mode() != tyglobal.RUN_MODE_ONLINE:
            result = get_wx_access_token_online()
        else:
            new_token = get_token_from_wx_server()
            result = new_token['access_token']
    ftlog.info('_wx get_wx_access_token result', result)
    return result


def getSHA1(token, timestamp, nonce, encrypt):
    """
    用SHA1算法生成安全签名
    @param token:  票据
    @param timestamp: 时间戳
    @param encrypt: 密文
    @param nonce: 随机字符串
    @return: 安全签名
    """
    try:
        sortlist = [token, timestamp, nonce, encrypt]
        sortlist.sort()
        sha = hashlib.sha1()
        sha.update("".join(sortlist))
        return 0, sha.hexdigest()
    except:
        return -1, None

def firstDemonstration(params):
    """
    接入客服首次验证
    """
    ftlog.info('_wx firstDemonstration in', params)
    scData = TyCachedConfig("contact", tyglobal.gameId()).getScConfig()
    loginInfo = scData['login']
    token = loginInfo['token']
    # 初始验证使用，每次添加一个接口都需要这么验证一次，才能正常提交
    echostr = params.get('echostr')
    signature = params.get('signature')
    timestamp = params.get('timestamp')
    nonce = params.get('nonce')
    ret, tmpsignature = getSHA1(token, timestamp, nonce, '')
    ftlog.info('_wx firstDemonstration result',
               'signature=', signature,
               'nonce=', nonce,
               'ret=', ret,
               'tmpsignature=', tmpsignature,
               'token=', token)
    if signature == tmpsignature:
        return echostr
    return None

def notice_me(text):
    """
    群发消息通知我自己
    """
    params = {
        "touser": "ocK8g5dFAOZfgTMwvLJTm1XQWBy8",
        "msgtype": 'text',
        "text": {
            "content": text
        }
    }
    postAnswer("ocK8g5dFAOZfgTMwvLJTm1XQWBy8", params)

def get_msg_param(answers_conf, msgtype, openId, sys="Android"):
    """
    获取消息参数
    @param msgtype:
    @return:
    """
    ftlog.debug('_wx get_msg_param in', answers_conf, msgtype, openId, sys)
    params = {}
    params['touser'] = openId
    params['msgtype'] = msgtype
    if msgtype == "text":
        params['text'] = {
            "content": answers_conf
        }
    elif msgtype == "image":
        db_media = mixDaoGameData.get_wx_media() or {}
        db_media_info = db_media.get(answers_conf['media'])
        if not db_media_info:
            return None
        if (db_media_info['created_at'] + 3*24*60*60) < int(time.time()):
            return None
        params["image"] = {
            "media_id": db_media_info['media_id']
        }
    elif msgtype == "link":
        link_cnf = answers_conf[sys]
        params["link"] = {
            "title": link_cnf["title"],
            "description": link_cnf["description"],
            "url": link_cnf["url"],
            "thumb_url": link_cnf["thumb_url"]
        }
    elif msgtype == "miniprogrampage":
        rand_answers_conf = random.sample(answers_conf, 1)
        db_media = mixDaoGameData.get_wx_media() or {}
        db_media_info = db_media.get(rand_answers_conf[0]['thumb_media'])
        if not db_media_info:
            return None
        if (db_media_info['created_at'] + 3 * 24 * 60 * 60) < int(time.time()):
            return None
        params["miniprogrampage"] = {
            "title": rand_answers_conf[0]['title'],
            "pagepath": rand_answers_conf[0]['pagepath'],
            "thumb_media_id": db_media_info['media_id']
        }
    ftlog.debug('_wx get_msg_param params', params, answers_conf, msgtype, openId)
    return params

def postAnswer(open_id, send_params):
    """
    将客服消息传到用户
    @param textmod:
    @return:
    """
    ftlog.debug('_wx postAnswer in', open_id, send_params)
    scData = TyCachedConfig("contact", tyglobal.gameId()).getScConfig()
    send_msg_conf = scData['send_msg']
    # 回复消息类型
    if not send_params:
        ftlog.info('_wx postAnswer no params')
        return
    accessToken = get_wx_access_token()
    if not accessToken:
        ftlog.info('_wx postAnswer no accessToken')
        return
    url = "https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={token}".format(token=accessToken)
    if send_msg_conf == "query":
        result = fthttp.queryHttp('POST', url, None, json.dumps(send_params, ensure_ascii=False), 5)
        ftlog.info('_wx postAnswer POST queryHttp result', result)
    else:
        fthttp.sendHttp('POST', url, None, json.dumps(send_params, ensure_ascii=False), 5)
        ftlog.info('_wx postAnswer POST sendHttp over', open_id)

def upload_image():
    """
    上传素材到腾讯服务器
    """
    scData = TyCachedConfig("contact", tyglobal.gameId()).getScConfig()
    media_conf = scData['media_file']
    for file_name, file_url in media_conf.items():
        db_media_data = mixDaoGameData.get_wx_media() or {}
        one_media_data = db_media_data.get(file_name, {})
        created_at = one_media_data.get('created_at', 0)
        if created_at + 68*60*60 > int(time.time()):
            continue
        image = requests.get(url=file_url)
        if image.content:
            accessToken = get_wx_access_token()
            if not accessToken:
                ftlog.info('_wx postAnswer no accessToken')
                return
            posturl = "https://api.weixin.qq.com/cgi-bin/media/upload?access_token={token}&type=image".format(token=accessToken)
            files = {
                "media": (file_name + '.jpg', image.content, 'image/jpg'),
            }
            res = requests.post(posturl, files=files).json()
            if 'created_at' in res:
                db_media_data[file_name] = {
                    'created_at': int(res['created_at']),
                    'media_id': res['media_id']
                }
                mixDaoGameData.set_wx_media(db_media_data)
            ftlog.info('_wx upload_image upload ', res)

def get_sys_by_pagepath(pagePath):
    """
    解析客服消息的pagePath，获取系统: iOS/Android
    """
    ftlog.debug('_wx get_sys_by_pagepath in', pagePath)
    if not pagePath:
        return None
    cleint_param = pagePath.split('?')
    if not cleint_param or len(cleint_param) < 2:
        return None
    params = cleint_param[1].split(',')
    if not params or len(params) < 2:
        return None
    if not params[0]:
        return None
    ftlog.debug('_wx get_sys_by_pagepath out', params)
    return params[0]

def get_auto_answer_conf(openId, msgType):
    """
    客服自动回复策略：
    1.没领取奖励，收到小卡片
    2.没领取奖励，收到文字或图片
    3.领取过
    @return:
    """
    scData = TyCachedConfig("contact", tyglobal.gameId()).getScConfig()
    auto_answer = scData['answers']['auto_answer']
    if not openId or not msgType:
        return auto_answer['2']
    db_data = DaoWordContact.getOneOpenId(openId) or {}
    is_reward_today = fttime.is_same_day(db_data.get('reward', 0), time.time())
    if is_reward_today:
        return auto_answer['3']
    if msgType == "miniprogrampage":
        # 更新用户发送小卡片时间
        DaoWordContact.updateOneOpenId(openId, "miniprogrampage", int(time.time()))
        return auto_answer['1']
    else:
        return auto_answer['2']

def answer(params):
    """
    回复消息
    @param gameId:
    @param request:
    @return:
    """
    ftlog.info('_wx answer in params ', params)
    # 初始验证使用，每次添加一个接口都需要这么验证一次，才能正常提交
    if params.get('echostr'):
        return firstDemonstration(params)
    # 回复
    if params.get('MsgType') and params.get('openid'):
        # 回复策略
        if params.get('MsgType') != "event":
            # 保存openId用于以后发召回消息
            DaoWordContact.addOpenId(params['openid'])
            # 检查素材是否过期
            upload_image()
            # 自动回复
            sys = get_sys_by_pagepath(params.get('PagePath')) or "Android"
            auto_answer_conf = get_auto_answer_conf(params.get('openid'), params.get('MsgType'))
            if "text" in auto_answer_conf:
                send_params = get_msg_param(auto_answer_conf["text"], "text", params['openid'], sys)
                ftcore.runOnceDelay(0.5, postAnswer, params['openid'], send_params)
            if "link" in auto_answer_conf:
                send_params = get_msg_param(auto_answer_conf["link"], "link", params['openid'], sys)
                ftcore.runOnceDelay(0.5, postAnswer, params['openid'], send_params)
            if "image" in auto_answer_conf:
                send_params = get_msg_param(auto_answer_conf["image"], "image", params['openid'], sys)
                ftcore.runOnceDelay(1, postAnswer, params['openid'], send_params)
            if "miniprogrampage" in auto_answer_conf:
                send_params = get_msg_param(auto_answer_conf["miniprogrampage"], "miniprogrampage", params['openid'], sys)
                ftcore.runOnceDelay(1, postAnswer, params['openid'], send_params)
    return "success"


def send_contact_msg(server_index):
    """
    给48小时联系客服服的用户发消息
    @return:
    """
    ftlog.info('_wx send_contact_msg in ', server_index)
    scData = TyCachedConfig("contact", tyglobal.gameId()).getScConfig()
    send_msg_conf = scData['answers']['send_all']
    gs_num = scData['gs_num']
    if server_index == 0:
        notice_me("开始发召回消息")
    for i in range(0, 1000):  # 默认最大遍历100万条
        if i % gs_num != server_index:
            continue
        all_openId = DaoWordContact.getThousandOpenId(i)
        for index, val in enumerate(all_openId):
            if val['lastContactTime'] + 47*60*60 < int(time.time()):
                DaoWordContact.delOpenId(val)
                continue
            # 发送消息
            send_params = get_msg_param(send_msg_conf, "miniprogrampage", val['openId'])
            postAnswer(val['openId'], send_params)
            # 打点
            tybireport.reportGameEvent('CHENGYUDGR_SEND_CONTECT_MSG', 0, 0, 0, 0, 0, 0, 0, 0, [], util.getClientId())
            ftcore.sleep(0.1)
        if len(all_openId) < 1000:
            break
    if server_index == 0:
        notice_me("结束发召回消息")
    ftlog.info('_wx send_contact_msg out')


# def post_template_msg(openId, templateId):
#     """
#     发送模板消息
#     """
#     accessToken = get_wx_access_token()
#     if not accessToken:
#         ftlog.info('_wx postAnswer no accessToken')
#         return -1
#     url = "https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={token}".format(token=accessToken)
#     param = {
#         "touser": openId,
#         "template_id": templateId,
#         "page": "index",
#         "data": {
#             "text": {
#                 "value": "1111"
#             }
#         }
#     }
#     result = fthttp.queryHttp('POST', url, None, json.dumps(param, ensure_ascii=False), 5)
#     ftlog.info('_wx postAnswer POST queryHttp result', result)
#
#
# def send_many_template_msg(server_index, templateId):
#     """
#     定时群发模板消息
#     @return:
#     """
#     ftlog.info('_wx send_template_msg in ', templateId)
#     scData = TyCachedConfig("contact", tyglobal.gameId()).getScConfig()
#     gs_num = scData['gs_num']
#     for i in range(0, 1000):  # 默认最大遍历100万条
#         if i % gs_num != server_index:
#             continue
#         thousand_data = DaoWordTemplate.getThousandData(i)
#         for index, val in enumerate(thousand_data):
#             if len(val['templateIds']) < 1:
#                 DaoWordTemplate.deleteOne(val)
#                 continue
#             if templateId not in val['templateIds']:
#                 continue
#             # 离线时间判断
#             # 发送消息
#             send_params = post_template_msg(val['openId'], templateId)
#             postAnswer(val['openId'], send_params)
#             # 打点
#             tybireport.reportGameEvent('CHENGYUDGR_SEND_TEMPLATE_MSG', 0, 0, 0, 0, 0, 0, 0, 0, [], util.getClientId())
#             ftcore.sleep(0.1)
#         if len(thousand_data) < 1000:
#             break
#     ftlog.info('_wx send_contact_msg out')
