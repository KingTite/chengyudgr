# -*- coding: utf-8 -*-

from freetime5.util import ftlog
from tuyoo5.core import tyrpcsdk, tyconfig, tyglobal, typlugin, tychecker
from tuyoo5.core.typlugin import pluginCross, gameRpcUtilOne
from tuyoo5.game import tybireport
from chengyudgr.entity.dao import UserDaoGameData, DaoWordComment, DaoRank, DaoRankInfo
from chengyudgr.rank.rank import Rank
from chengyudgr import util
import time

from . import _base_game_data, _activity, _notice, _shop



class ChengyudgrPluginSrvutil(typlugin.TYPlugin):

    def __init__(self):
        super(ChengyudgrPluginSrvutil, self).__init__()


    def destoryPlugin(self):
        UserDaoGameData.finalize()
        DaoWordComment.finalize()
        DaoRank.finalize()
        DaoRankInfo.finalize()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_GAME_UTIL])
    def initPluginBefore(self):
        UserDaoGameData.initialize()
        DaoWordComment.initialize()
        DaoRank.initialize()
        DaoRankInfo.initialize()

    @typlugin.markPluginEntry(initAfterConfig=[tyglobal.SRV_TYPE_GAME_UTIL])
    def initPluginAfter(self):
        pass

    # 获取玩家详细数据
    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL, export=1)
    def getGameDataInfo(self, userId):
        db_data = UserDaoGameData.get_game_data(userId)
        return db_data

    # 基础游戏数据
    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL, export=1)
    def updateBaseGameData(self, userId, stage_data):
        try:
            mo = _base_game_data.update_base_game_data(userId, stage_data)
        except:
            ftlog.error()
            mo = {'code': 10}
        return mo

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL, export=1)
    def getBaseGameData(self, userId):
        try:
            mo = _base_game_data.get_base_game_data(userId)
        except:
            ftlog.error()
            mo = {'code': 10}
        return mo

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL, export=1)
    def updataOneBaseGameData(self, userId, questionId, data_key, data_val, is_item):
        try:
            mo = _base_game_data.updata_one_base_game_data(userId, questionId, data_key, data_val, is_item)
        except:
            ftlog.error()
            mo = {'code': 10}
        return mo

    # 基础用户数据
    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL, export=1)
    def updateBaseUserData(self, userId, name, icon):
        try:
            mo = _base_game_data.set_base_user_data(userId, name, icon)
        except:
            ftlog.error()
            mo = {'code': 10}
        return mo


    # 用户评论
    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL, export=1)
    def doComment(self, userId, comment):
        try:
            data = DaoWordComment.addComment(userId, comment)
            ftlog.debug('doComment DaoWordComment.addComment = ', data)
            return {'code': 0}
        except:
            ftlog.error()
            return {'code': -1}

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL, export=1)
    def getComments(self, userId):
        try:
            comments = DaoWordComment.getComments()
            data = []
            if 'comments' in comments:
                for c in comments['comments']:
                    c.pop('_id')
                    data.append(c)
            ftlog.debug('doComment DaoWordComment.getComments = ', data)
            return data
        except:
            ftlog.error()
            return {'code': -1}

    # 每日解密活动
    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL, export=1)
    def updateMrjm(self, userId, state, flower, allTime):
        try:
            mo = _activity.update_mrjm(userId, state, flower, allTime)
        except:
            ftlog.error()
            mo = {'code': 10}
        return mo

    # 获取排行榜
    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL, export=1)
    def getRankInfo(self, userId, rank_name):
        try:
            mo = Rank.get_rank_info(userId, rank_name)
        except:
            ftlog.error()
            mo = {'code': 10}
        return mo

    # 更新科举活动数据
    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL, export=1)
    def updateKejvData(self, userId, kejv_data):
        try:
            mo = _activity.updata_kejv_data(userId, kejv_data)
        except:
            ftlog.error()
            mo = {'code': 10}
        return mo

    # 获取科举活动数据
    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL, export=1)
    def geteKejvData(self, userId):
        try:
            mo = _activity.get_kejv_data(userId)
        except:
            ftlog.error()
            mo = {'code': 10}
        return mo

    # 更新极限玩法数据
    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL, export=1)
    def updateHardData(self, userId, hard_data):
        try:
            mo = _activity.updata_hard_data(userId, hard_data)
        except:
            ftlog.error()
            mo = {'code': 10}
        return mo

    # 获取极限玩法数据
    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL, export=1)
    def geteHardData(self, userId):
        try:
            mo = _activity.get_hard_data(userId)
        except:
            ftlog.error()
            mo = {'code': 10}
        return mo

    # 登录接口
    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL, export=1)
    def longin(self, userId, login_param):
        try:
            # 获取公告通知
            notice_data = _notice.get_notice(userId, login_param)
            # 获取玩家基础游戏数据
            base_geme_data = UserDaoGameData.get_base_game_data(userId) or {}
            # 设置每日登录次数
            pluginCross.day1st.setLoginCount(userId)
            # 更新玩家基础数据
            _base_game_data.set_base_user_data(userId, login_param)
            # 补单数据
            replacement_order = _shop.replacement_order(userId)
            # 充值金额
            pay_money = _shop.get_all_pay_money(userId)
            # 极限玩法
            hard_data = UserDaoGameData.get_hard_data(userId) or {}
            # 是否免广告
            ad_remove = UserDaoGameData.get_ad_remove(userId)
            # 每日解谜鲜花数量
            flower = UserDaoGameData.get_mrjm_flower(userId)
            # 最后更新游戏数据时间
            update_diff_sec = 0
            update_time = UserDaoGameData.get_update_time(userId) or 0
            if update_time > 0:
                update_diff_sec = int(time.time()) - int(update_time)
            # 返回数据
            mo = {
                'code': 0,
                'notice_data': notice_data,
                'base_geme_data': base_geme_data,
                "replacement_order": replacement_order,
                "pay_money": pay_money,
                "hard_data": hard_data,
                "ad_remove": ad_remove,
                "flower": flower,
                "update_diff_sec": update_diff_sec
            }
        except:
            ftlog.error()
            mo = {'code': 10}
        return mo

    # sdk支付成功回调
    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL, export=1)
    def sdkPaySuccess(self, userId, sdk_param):
        try:
            mo = _shop.sdk_pay_success(userId, sdk_param)
        except:
            ftlog.error()
            mo = {'code': 10}
        return mo

    # 请求待发货订单
    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL, export=1)
    def getReadyOrder(self, userId, orderId):
        try:
            mo = _shop.get_ready_order(userId, orderId)
        except:
            ftlog.error()
            mo = {'code': 10}
        return mo


    # 前端发货成功
    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL, export=1)
    def orderComplete(self, userId, order_info):
        try:
            mo = _shop.order_complete(userId, order_info)
        except:
            ftlog.error()
            mo = {'code': 10}
        return mo

    # 获取商品列表
    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL, export=1)
    def getProductList(self, userId, shopVersion):
        try:
            mo = _shop.get_product_list(userId, shopVersion)
        except:
            ftlog.error()
            mo = {'code': 10}
        return mo

    # 增加收藏
    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL, export=1)
    def updateCollectIdiomId(self, userId, collectList):
        try:
            ftlog.debug('updateCollectIdiomId in', userId, collectList)
            db_collect = UserDaoGameData.get_collect(userId) or []
            for idiom_id in collectList:
                if idiom_id not in db_collect:
                    db_collect.append(idiom_id)
            UserDaoGameData.set_collect(userId, db_collect)
            if len(db_collect) > 3000:
                tybireport.reportGameEvent('CHENGYUDGR_COLLECT',
                                           userId,
                                           tyglobal.gameId(),
                                           0, 0, 0, 0,
                                           0, len(db_collect),
                                           [],
                                           util.getClientId())
            mo = {'code': 0}
        except:
            ftlog.error()
            mo = {'code': 10}
        return mo

    # 获取收藏
    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL, export=1)
    def getCollectIdiomId(self, userId):
        try:
            db_collect = UserDaoGameData.get_collect(userId) or []
            mo = {
                'code': 0,
                'data': db_collect
            }
        except:
            ftlog.error()
            mo = {'code': 10}
        return mo