# -*- coding: utf-8 -*-
from freetime5.util import ftlog
from tuyoo5.core import typlugin, tyglobal
from tuyoo5.plugins.weakdata.weakdata import TyPluginWeakData

_DEBUG, debug = ftlog.getDebugControl(__name__)


class PluginDay1st(TyPluginWeakData):
    def __init__(self):
        super(PluginDay1st, self).__init__()

    def destoryPlugin(self):
        super(PluginDay1st, self).destoryPlugin()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_GAME_UTIL])
    def initPluginBefore(self):
        super(PluginDay1st, self).initPluginBefore()

    @typlugin.markPluginEntry(export=1)
    def getActivityMrjm(self, userId):
        """
        获取每日解谜活动数据
        """
        datas = self.getDay1stDatas(userId)
        data_mrjm = datas.get('activity_mrjm', {})
        return data_mrjm

    @typlugin.markPluginEntry(export=1)
    def setActivityMrjm(self, userId, data_mrjm):
        """
        设置每日解谜活动数据
        """
        datas = self.getDay1stDatas(userId)
        datas['activity_mrjm'] = data_mrjm
        self.setDay1stDatas(userId, datas)

    @typlugin.markPluginEntry(export=1)
    def setLoginCount(self, userId):
        """
        设置每日登陆次数
        """
        datas = self.getDay1stDatas(userId)
        count = datas.get('login_count', 0)
        datas['login_count'] = count + 1
        self.setDay1stDatas(userId, datas)
        ftlog.debug("PluginDay1st setLoginCount ", userId, count)

    @typlugin.markPluginEntry(export=1)
    def getLoginCount(self, userId):
        """
        获取每日登陆次数
        """
        datas = self.getDay1stDatas(userId)
        count = datas.get('login_count', 0)
        ftlog.debug("PluginDay1st getLoginCount ", userId, count)
        return count

    @typlugin.markPluginEntry(export=1)
    def setNoticeTimes(self, userId, notice_id):
        """
        设置每日查看固定公告次数
        """
        datas = self.getDay1stDatas(userId)
        notice_times_d = datas.get('notice_times', {})
        times = notice_times_d.get(str(notice_id), 0)
        times += 1
        notice_times_d[str(notice_id)] = times
        datas['notice_times'] = notice_times_d
        self.setDay1stDatas(userId, datas)
        ftlog.debug("PluginDay1st setNoticeTimes ", userId, notice_id, times)

    @typlugin.markPluginEntry(export=1)
    def getNoticeTimes(self, userId, notice_id):
        """
        获取每日查看固定公告次数
        """
        datas = self.getDay1stDatas(userId)
        notice_times_d = datas.get('notice_times', {})
        times = notice_times_d.get(str(notice_id), 0)
        return times
