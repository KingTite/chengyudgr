# -*- coding=utf-8  -*-

from freetime5.twisted.ftlock import lockargname
from freetime5.util import ftlog
from freetime5.util import fttime
from chengyudgr.entity.dao import UserDaoGameData
from chengyudgr.rank.rank import Rank
import time
from tuyoo5.game import tybireport
from tuyoo5.core import tyrpcsdk, tyconfig, tyglobal,tyrpchall
from tuyoo5.core.tyconfig import TyCachedConfig
from chengyudgr import util

_DEBUG, debug = ftlog.getDebugControl(__name__)

'''
当前关卡相关数据
'''

@lockargname("_base_game_data", "userId")
def update_base_game_data(userId, game_data):
    """
    更新基础游戏数据变化
    """
    # 当日关卡进度
    db_data = UserDaoGameData.get_base_game_data(userId) or {}
    # 上传进度是0
    if "questionId" not in game_data:
        return {'code': 1}
    #  超过最大关卡
    game_config = TyCachedConfig('game_config', tyglobal.gameId()).getScConfig()
    if game_data['questionId'] > game_config.get('max_questionId'):
        return {'code': 2}
    # 上传关卡进度小于数据库
    if db_data.get('questionId', 0) > game_data['questionId']:
        return {'code': 3}
    # 只增不减的数据
    game_data['OfficialLevel'] = max(db_data.get('OfficialLevel', 0), game_data.get('OfficialLevel', 0))
    game_data['houseLevel'] = max(db_data.get('houseLevel', 0), game_data.get('houseLevel', 0))
    # 门客限制
    wifeArray = game_data.get('wifeArray', [])
    if not isinstance(wifeArray, list) or len(wifeArray) < 1:
        game_data['wifeArray'] = db_data.get('wifeArray', [])
    # 获取每日进度
    if not db_data:
        game_data['today_progress'] = game_data['questionId']
    else:
        # 与数据库关卡对比,上传关卡限制
        add = game_data['questionId'] - db_data.get('questionId', 0)
        diff_time = int(time.time()) - db_data.get('updata_time', 0)
        min_stage_time = game_config.get('min_stage_time', 0)  # 通关最短时间限制
        if (add * min_stage_time) >= diff_time:
            ftlog.warn("today_progress to many: ", userId, add, diff_time)
            return {'code': 4}
        # 每日进度
        isSameDay = fttime.is_same_day(db_data.get('updata_time', 0), time.time())
        if not isSameDay:
            game_data['today_progress'] = game_data['questionId'] - db_data.get('questionId', 0)
        else:
            game_data['today_progress'] = db_data.get('today_progress', 0) + (game_data['questionId'] - db_data.get('questionId', 0))

    game_data['updata_time'] = int(time.time())
    # 更新数据库
    UserDaoGameData.set_base_game_data(userId, game_data)

    # 增加每日进度排行榜
    if game_data['today_progress'] < game_config.get('max_day_questionId'):  # 每日上传关卡异常
        Rank.add_score_to_rank("cydgr_stage_day_progress_rank", userId, int(game_data['today_progress']))
    # 增加进度总排行榜
    Rank.add_score_to_rank("cydgr_stage_rank", userId, int(game_data['questionId']))

    ftlog.info('update_base_game_data out ->', userId, game_data)

    return {'code': 0}


@lockargname("_base_game_data", "userId")
def get_base_game_data(userId):
    """
    获取最新关卡数据
    """
    geme_data = UserDaoGameData.get_base_game_data(userId) or {}

    ftlog.debug('get_base_game_data->', userId, geme_data)

    result = {
        'code': 0,
        'data': geme_data
    }
    return result


@lockargname("_base_game_data", "userId")
def updata_one_base_game_data(userId, questionId, data_key, data_val, is_item):
    """
    更新单个数据 base_game_data
    """
    ftlog.debug('updata_one_base_game_data in ->', userId, questionId, data_key, data_val, is_item)

    # 无关卡id返回
    if not questionId:
        return {'code': 1}
    # 值不为空
    if (not data_val) and (data_val != 0):
        return {'code': 2}
    # db关卡进度
    db_data = UserDaoGameData.get_base_game_data(userId) or {}

    # 关卡进度小于数据库进度
    if questionId < db_data.get('questionId', 0):
        return {'code': 3}

    # 上传物品
    if is_item:
        prop = db_data.get('prop', {})
        prop[data_key] = data_val
        db_data['prop'] = prop
        # 更新数据库
        UserDaoGameData.set_base_game_data(userId, db_data)
    else:
        # 上传关卡进度
        if data_key == "questionId":
            # 关卡数据类型判断
            if not isinstance(data_val, int):
                return {'code': 1}
            # 超过最大关卡
            game_config = TyCachedConfig('game_config', tyglobal.gameId()).getScConfig()
            if data_val > game_config.get('max_questionId'):
                return {'code': 4}
            # 上传关卡进度小于数据库
            if data_val < db_data.get('questionId'):
                return {'code': 3}
            # 获取每日进度
            if not db_data:
                db_data['today_progress'] = data_val
            else:
                # 与数据库关卡对比,上传关卡限制
                add = data_val - db_data.get('questionId', 0)
                diff_time = int(time.time()) - db_data.get('updata_time', 0)
                min_stage_time = game_config.get('min_stage_time', 0)  # 通关最短时间限制
                if (add * min_stage_time) >= diff_time:
                    return {'code': 4}
                # 每日进度
                isSameDay = fttime.is_same_day(db_data.get('updata_time', 0), time.time())
                if not isSameDay:
                    db_data['today_progress'] = data_val - db_data.get('questionId', 0)
                else:
                    db_data['today_progress'] = db_data.get('today_progress', 0) + (data_val - db_data.get('questionId', 0))

            db_data['updata_time'] = int(time.time())
            db_data['questionId'] = data_val

            # 更新数据库
            UserDaoGameData.set_base_game_data(userId, db_data)

            # 增加每日进度排行榜
            if db_data['today_progress'] < game_config.get('max_day_questionId'):  # 每日上传关卡异常
                Rank.add_score_to_rank("cydgr_stage_day_progress_rank", userId, int(db_data['today_progress']))
            # 增加进度总排行榜
            Rank.add_score_to_rank("cydgr_stage_rank", userId, data_val)

        else:
            db_data[data_key] = data_val
            # 更新数据库
            UserDaoGameData.set_base_game_data(userId, db_data)
    # 打点
    if is_item:
        tybireport.reportGameEvent('CHENGYUDGR_SEND_TEMPLATE_MSG', userId, int(data_key), 0, 0, 0, 0, 0, 0, [], util.getClientId())
    ftlog.info('updata_one_base_game_data out ->', userId, questionId, data_key, data_val, is_item)

    return {'code': 0}

@lockargname("_base_game_data", "userId")
def set_base_user_data(userId, user_data):
    """
    设置用户基础信息
    """
    if not user_data:
        return {'code': 1}

    if not user_data.get('is_wx'):
        return {'code': 1}

    if not user_data.get('icon'):
        return {'code': 1}

    # 用户是否存在
    creat_time = tyrpcsdk.getUserDatas(userId, tyrpchall.UserKeys.ATT_CREATE_TIME)
    if not creat_time or not creat_time.get('createTime'):
        return {'code': 1}
    
    # 用户是否有头像
    purl = tyrpcsdk.getUserDatas(userId, tyrpchall.UserKeys.ATT_PURL)
    if not purl or not purl.get('purl'):
        return {'code': 1}

    user_data['icon'] = purl.get('purl')

    UserDaoGameData.set_base_user_data(userId, user_data) or {}

    ftlog.debug('set_base_user_data->', userId, user_data)

    result = {
        'code': 0
    }
    return result


@lockargname("_base_game_data", "userId")
def get_base_user_data(userId):
    """
    获取用户基础信息
    """
    user_data = UserDaoGameData.get_base_user_data(userId) or {}

    ftlog.debug('get_base_user_data->', userId, user_data)

    result = {
        'code': 0,
        'data': user_data
    }
    return result
