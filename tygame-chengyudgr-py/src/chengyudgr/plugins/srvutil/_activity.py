# -*- coding=utf-8  -*-

"""
活动相关
"""

from freetime5.util import ftlog, fttime
from tuyoo5.core.typlugin import pluginCross, gameRpcUtilOne
from chengyudgr.rank.rank import Rank
from chengyudgr.entity.dao import UserDaoGameData
from freetime5.twisted.ftlock import lockargname
from tuyoo5.core.tyconfig import TyCachedConfig
from tuyoo5.core import tyglobal
import time


# 每日解谜
@lockargname("_activity", "userId")
def update_mrjm(userId, state, flower, all_time):
    """
    --每日时长排行榜
    --总鲜花排行榜
    @param state: 关卡开始：0，关卡挑战中：1  关卡结束：2
    @param flower: 获得鲜花数量
    @return:
    """
    ftlog.debug('update_mrjm->', userId, state, flower, all_time)
    game_config = TyCachedConfig('game_config', tyglobal.gameId()).getScConfig()
    data_mrjm = pluginCross.day1st.getActivityMrjm(userId) or {}

    if data_mrjm.get('end_time'):
        # 今日挑战过了
        return {"code": 1}

    if state == 2:
        # 关卡结束，计算总时长
        data_mrjm['end_time'] = int(time.time())
        pluginCross.day1st.setActivityMrjm(userId, data_mrjm)
        # 闯关总时长异常
        if all_time < game_config.get('max_mrjm_time'):
            return {'code': 4}
        # 加入排行榜
        Rank.add_score_to_rank("cydgr_mrjm_time_rank", userId, all_time)

    # 增加鲜花总数
    if flower > 0:
        data_mrjm['flower'] = data_mrjm.get('flower', 0) + flower
        # 鲜花异常
        if data_mrjm['flower'] > game_config.get('max_mrjm_flower'):
            return {'code': 4}
        pluginCross.day1st.setActivityMrjm(userId, data_mrjm)

        db_flower = UserDaoGameData.get_mrjm_flower(userId) or 0
        now_flowe = db_flower + flower
        UserDaoGameData.set_mrjm_flower(userId, now_flowe)
        # 加入排行榜
        Rank.add_score_to_rank("cydgr_mrjm_flower_rank", userId, now_flowe)

    return {"code": 0}


# 科举活动
@lockargname("_activity", "userId")
def updata_kejv_data(userId, kejv_data):
    """
    更新科举活动数据
    """
    game_config = TyCachedConfig('game_config', tyglobal.gameId()).getScConfig()

    # 加入科举赛季排行榜
    if kejv_data.get('SeasonScore'):
        if kejv_data.get('SeasonScore') > game_config.get('max_seasonScore'):
            return {'code': 4}
        Rank.add_score_to_rank("cydgr_kejv_rank", userId, kejv_data.get('SeasonScore'))
    # 更新数据库
    UserDaoGameData.set_kejv_data(userId, kejv_data)

    ftlog.debug('updata_kejv_data->', userId, kejv_data)

    return {'code': 0}


@lockargname("_activity", "userId")
def get_kejv_data(userId):
    """
    获取科举活动数据
    """
    # 更新数据库
    kejv_data = UserDaoGameData.get_kejv_data(userId)

    ftlog.debug('get_kejv_data->', userId, kejv_data)

    result = {
        'code': 0,
        'data': kejv_data
    }
    return result


# 极限玩法
@lockargname("_activity", "userId")
def updata_hard_data(userId, hard_data):
    """
    更新极限玩法数据
    """
    if not hard_data.get('hardQuestionId'):
        return {'code': 1}
    # 异常进度
    game_config = TyCachedConfig('game_config', tyglobal.gameId()).getScConfig()
    if hard_data['hardQuestionId'] > game_config.get('max_hard_questionId'):
        return {'code': 4}

    db_data = UserDaoGameData.get_hard_data(userId) or {}
    # 保存高进度
    if hard_data['hardQuestionId'] < db_data.get('hardQuestionId', 0):
        return {'code': 1}
    # 获取每日进度
    if not db_data:
        hard_data['today_progress'] = hard_data['hardQuestionId']
    else:
        isSameDay = fttime.is_same_day(db_data.get('updata_time', 0), time.time())
        if not isSameDay:
            hard_data['today_progress'] = hard_data['hardQuestionId'] - db_data.get('hardQuestionId', 0)
        else:
            hard_data['today_progress'] = db_data.get('today_progress', 0) + (
                    hard_data['hardQuestionId'] - db_data.get('hardQuestionId', 0))
    hard_data['updata_time'] = int(time.time())

    # 更新数据库
    UserDaoGameData.set_hard_data(userId, hard_data)
    # 加入极限玩法排行榜
    Rank.add_score_to_rank("cydgr_hard_rank", userId, hard_data.get('hardQuestionId'))
    Rank.add_score_to_rank("cydgr_hard_day_rank", userId, hard_data.get('today_progress'))

    ftlog.debug('updata_hard_data->', userId, hard_data)

    return {'code': 0}


@lockargname("_activity", "userId")
def get_hard_data(userId):
    """
    获取极限玩法数据
    """
    # 更新数据库
    hard_data = UserDaoGameData.get_hard_data(userId)

    ftlog.debug('get_hard_data->', userId, hard_data)

    result = {
        'code': 0,
        'data': hard_data
    }
    return result
