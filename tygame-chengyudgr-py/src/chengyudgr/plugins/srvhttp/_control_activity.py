# -*- coding=utf-8  -*-


from freetime5.util import ftlog
from tuyoo5.core.typlugin import pluginCross, gameRpcUtilOne
from tuyoo5.core.tyconfig import TyCachedConfig
from tuyoo5.core import tyglobal, typlugin
from chengyudgr.entity.dao import mixDaoGameData
from chengyudgr.rank.rank import Rank
from datetime import datetime, timedelta
import time
import math
import calendar

_DEBUG, debug = ftlog.getDebugControl(__name__)

def get_time(week, hour):
    """
    当前周的时间戳
    """
    minute = 0
    second = 0
    if hour == 24:
        hour = 23
        minute = 59
        second = 59
    now = datetime.utcfromtimestamp(time.time()) + timedelta(hours=8)  # 北京时间
    start = now - timedelta(days=now.isoweekday())  # 上个周日时间
    start = start + timedelta(days=week)  # 配置的星期
    start = start.replace(hour=hour, minute=minute, second=second)  # 固定星期的固定小时
    # start = start - timedelta(hours=8)  # 海外转成UTC
    start_s = start.timetuple()
    time_s = int(time.mktime(start_s))  # 时间戳
    ftlog.debug('_activity.get_time->', start_s, time_s)
    return time_s

def get_monthrange():
    """
    获取当月天数
    """
    now = datetime.utcfromtimestamp(time.time()) + timedelta(hours=8)  # 北京时间
    monthRange = calendar.monthrange(now.year, now.month)
    ftlog.debug('_activity.get_monthrange->', monthRange)
    return monthRange[1]


def get_month_time(day):
    """
    当前月的时间戳
    """
    now = datetime.utcfromtimestamp(time.time()) + timedelta(hours=8)  # 北京时间
    # 本月第几天
    diff_day = now.day - day
    start = now - timedelta(days=diff_day)  # 开启日的时间
    start = start.replace(hour=0, minute=0, second=0)  # 固定星期的固定小时
    # start = start - timedelta(hours=8)  # 海外转成UTC
    start_s = start.timetuple()
    time_s = int(time.mktime(start_s))  # 时间戳
    ftlog.debug('_activity.get_month_time->', start_s, time_s)
    return time_s


def get_list_info(file_name, _id):
    """
    获取列表中的值
    """
    cnf = TyCachedConfig(file_name, tyglobal.gameId()).getScConfig()
    for val in cnf:
        if _id == val['id']:
            return val
    return None

def get_zhengji_activity_info(activity_id=20002):
    """
    获取政绩活动信息
    @return:
    """
    # 当前活动Id
    cnf_activity = get_list_info('control_activity', activity_id)
    cnf_zhengji = TyCachedConfig('zhengji_activity', tyglobal.gameId()).getScConfig()
    db_zhengji = mixDaoGameData.get_season_data(activity_id) or {}

    if not cnf_activity or not cnf_zhengji:
        return {}

    cur_id = 11101
    now_time = time.time()
    month_days = get_monthrange()
    is_update_db = False
    if db_zhengji:
        star_time = db_zhengji['start_time']
        end_time = db_zhengji['end_time']
        cur_id = db_zhengji['cur_season_id']
        if now_time > end_time:
            cur_id = cnf_zhengji[str(cur_id)]['next']
            is_update_db = True
    else:
        star_time = get_month_time(cnf_activity['open_time'][0])
        end_time = star_time + cnf_activity['open_diff']
        is_update_db = True
    # 更新数据库
    if is_update_db:
        if now_time > end_time:
            star_time = star_time + (month_days * 24 * 60 * 60)
            end_time = star_time + cnf_activity['open_diff']
        db_zhengji = {
            'activity_id': 20002,
            'start_time': star_time,
            'end_time': end_time,
            'cur_season_id': cur_id,
        }
        set_activity_info(activity_id, db_zhengji)
    # 返回详情
    if now_time >= star_time and now_time <= end_time:
        week_index = math.ceil((now_time - star_time) / (7 * 24 * 60 * 60))
        result = {
            'activity_id': 20002,
            "cur_season_id": cur_id,
            "isOpen": True,
            "week_index": int(week_index)
        }
        return result
    else:
        result = {
            'activity_id': 20002,
            "cur_season_id": cur_id,
            "isOpen": False,
            "week_index": 0
        }
        return result


def get_season_data(activity_id):
    """
    获取科举活动信息
    """
    # 获取活动控制配置信息
    cnf_activity = get_list_info('control_activity', activity_id)
    if not cnf_activity:
        return None
    if 'file_name' not in cnf_activity:
        return None
    # 获取数据库信息
    db_season = mixDaoGameData.get_season_data(activity_id) or {}
    now_time = time.time()
    ftlog.debug("get_season_data db_season-> ", now_time, activity_id, db_season)
    if db_season:
        # 赛季尚未开始
        if now_time < db_season['start_time']:
            db_season['countdown'] = 0
            db_season['open'] = False
            return db_season
        # 正在当前赛季
        if now_time >= db_season['start_time'] and now_time <= db_season['end_time']:
            db_season['open'] = True
            db_season['countdown'] = int(db_season['end_time'] - now_time)
            return db_season
        # 设置下一个赛季开始
        if now_time > db_season['end_time']:
            # 清空赛季排行榜
            Rank.resetRank(2)
            # 获取当前赛季配置
            cnf_season = get_list_info(cnf_activity['file_name'], db_season['cur_season_id'])
            curr_season_id = cnf_season.get('next_id')
            if not curr_season_id:
                return None
            start_time = get_time(cnf_activity['open_time'][0], cnf_activity['open_hour'])
            if start_time == db_season['start_time']:
                start_time += 7*24*60*60
            end_time = start_time + cnf_activity['open_diff']
            db_season = {
                'activity_id': activity_id,
                'start_time': start_time,
                'end_time': end_time,
                'cur_season_id': curr_season_id
            }
            if now_time < start_time or now_time > end_time:
                db_season['countdown'] = 0
                db_season['open'] = False
            else:
                db_season['countdown'] = int(end_time - now_time)
                db_season['open'] = True
            mixDaoGameData.set_season_data(activity_id, db_season)
            return db_season
    else:
        # 初始化赛季（默认第一赛季下次开始）
        start_time = get_time(cnf_activity['open_time'][0], cnf_activity['open_hour'])
        end_time = start_time + cnf_activity['open_diff']
        is_open = False
        countdown = 0
        if now_time >= start_time and now_time <= end_time:
            countdown = int(end_time - now_time)
            is_open = True
        elif now_time > end_time:
            start_time += 7*24*60*60
            end_time = start_time + cnf_activity['open_diff']
        db_season = {
            'activity_id': activity_id,
            'start_time': start_time,
            'end_time': end_time,
            'cur_season_id': 20001,
            'open': is_open,
            'countdown': countdown
        }
        mixDaoGameData.set_season_data(activity_id, db_season)
        return db_season

def set_activity_info(activity_id, db_season):
    """
    设置活动数据
    """
    mixDaoGameData.set_season_data(activity_id, db_season)

def get_week_activity(activity_id):
    """
    获取每周活动
    """
    cnf_activity = get_list_info('control_activity', activity_id)
    now_time = time.time()
    result = {}
    for val in cnf_activity['open_time']:
        start_time = get_time(val, cnf_activity['open_hour'])
        end_time = start_time + cnf_activity['open_diff']
        if now_time < start_time:
            result = {
                'activity_id': activity_id,
                'start_time': start_time,
                'end_time': end_time,
                'open': False
            }
            break
        elif now_time >= start_time and now_time <= end_time:
            result = {
                'activity_id': activity_id,
                'start_time': start_time,
                'end_time': end_time,
                'open': True
            }
            break
    if not result:
        start_time = get_time(cnf_activity['open_time'][0], cnf_activity['open_hour'])
        end_time = start_time + cnf_activity['open_diff']
        result = {
            'activity_id': activity_id,
            'start_time': start_time,
            'end_time': end_time,
            'open': False
        }
    return result


def get_all_activity_data(activity_id):
    """
    获取全部活动开启状态
    @return:
    """
    result = {}
    if activity_id:
        if 20002 == activity_id:
            # 政绩活动
            activity_data = get_zhengji_activity_info(activity_id)
            ftlog.debug('get_all_activity_data result ->', activity_data)
            result = activity_data
    else:
        # 科举考试兼容处理
        result_activity = []
        # 科举考试 20001
        activity_data = get_season_data(20001)
        # 返回前端要的格式
        activity_data['start_time'] = activity_data['start_time'] * 1000
        activity_data['end_time'] = activity_data['end_time'] * 1000
        result_activity.append(activity_data)
        result = result_activity
        
    ftlog.debug('get_all_activity_data result ->', result)
    return result

