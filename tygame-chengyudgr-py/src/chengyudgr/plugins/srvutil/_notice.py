# -*- coding=utf-8  -*-

from freetime5.util import ftlog
from tuyoo5.core.typlugin import pluginCross, gameRpcUtilOne
from tuyoo5.core.tyconfig import TyCachedConfig
from tuyoo5.core import tyglobal, typlugin
from freetime5.twisted.ftlock import lockargname
from chengyudgr.entity.dao import UserDaoGameData

import time

"""
游戏公告
"""
# 每日首次登录
DAY_FIRST_LOGIN = 1
# 每次登录
EVERY_TIME_LOGIN = 2
# 版本限制
VERSION_LIMT = 3
# clientId限制
CLIENTID_LIMIT = 4
# 每天限制通知次数
NOTICE_TIMES = 5
# 关卡等级限制
STAGE_LIMIT = 6


# 每日首次登录
def is_today_first_login(userId):
    """
    每日首次登录
    """
    day_longin_count = pluginCross.day1st.getLoginCount(userId)
    if day_longin_count > 0:
        return False
    else:
        return True


# 版本号判断
def is_equal_version(limit_version, _version):
    """
    版本号判断
    """
    if not limit_version or not _version:
        return False

    if str(limit_version) == str(_version):
        return True
    else:
        return False


# clientId判断
def is_equal_clientId(limit_clientId, _clientId):
    """
    clientId是否相等
    """
    if not limit_clientId or not _clientId:
        return False
    if str(limit_clientId) == str(_clientId):
        return True
    else:
        return False


# 每天限制通知次数
def is_limit_notice_times(userId, noticeId, limitTimes):
    """
    每天限制通知次数
    """
    notice_times = pluginCross.day1st.getNoticeTimes(userId, noticeId)
    if notice_times < limitTimes:
        return True
    else:
        return False


# 关卡等级限制
def is_stage_limit(userId, limit_stage):
    """
    关卡控制
    """
    geme_data = UserDaoGameData.get_base_game_data(userId) or {}
    stage = geme_data.get('questionId')
    if stage >= limit_stage:
        return True
    else:
        return False


# 判断推送条件
def notice_push_condition(userId, notice_id, params, c_type, c_param):
    ftlog.debug('_notice notice_push_condition in ->', userId, params, c_type, c_param)
    # 每日首次登录
    try:
        if c_type == DAY_FIRST_LOGIN:
            return is_today_first_login(userId)
        # 每次登录
        elif c_type == EVERY_TIME_LOGIN:
            return True
        # 版本号判断
        elif c_type == VERSION_LIMT:
            return is_equal_version(params.get('version'), c_param)
        # clientId判断
        elif c_type == CLIENTID_LIMIT:
            return is_equal_clientId(params.get('clientId'), c_param)
        # 每日通知次数
        elif c_type == NOTICE_TIMES:
            return is_limit_notice_times(userId, notice_id, c_param)
        # 关卡等级限制
        elif c_type == STAGE_LIMIT:
            return is_stage_limit(userId, c_param)
        # 未知条件
        else:
            return False
    except:
        return False


# 判断公告有效时间
def notice_time_condition(start_stamp, end_stamp):
    """
    公告有效时间判断
    """
    now_time = time.time()

    ftlog.debug('_notice notice_time_condition->', now_time, start_stamp, end_stamp)

    if now_time >= start_stamp and now_time < end_stamp:
        return True
    else:
        return False


# 获取公告信息
@lockargname("_notice", "userId")
def get_notice(userId, params):
    """
    获取全部可推送的公告
    """
    ftlog.debug('_notice get_notice in ->', userId, params)

    cnf_notice = TyCachedConfig("cydgr_notice", tyglobal.gameId()).getScConfig()
    notice_list = []
    # 遍历所有公告配置
    for val in cnf_notice:
        ftlog.debug('_notice get_notice val->', val, val.get('start_time'), val.get('end_time'))
        # 推送是否达成全部推送条件判断
        is_complete_all_condition = True
        for one_contition in val['push_contition']:
            if not notice_push_condition(userId, val['id'], params, int(one_contition['type']),
                                         one_contition.get('param')):
                is_complete_all_condition = False
                break
        if not is_complete_all_condition:
            continue
        # 判断公告时间是否过期
        if val.get('start_time_s') and val.get('end_time_s'):
            is_valid = notice_time_condition(val['start_time_s'], val['end_time_s'])
            if not is_valid:
                continue
        # 设置每日通知次数
        pluginCross.day1st.setNoticeTimes(userId, val['id'])
        # 可以推送
        notice_list.append(val)

    ftlog.debug('_notice get_notice out ->', notice_list)
    return notice_list
