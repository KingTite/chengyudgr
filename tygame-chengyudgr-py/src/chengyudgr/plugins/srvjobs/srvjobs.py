# -*- coding: utf-8 -*-

from datetime import datetime
from freetime5.util import ftlog
from freetime5.twisted import ftcore
from freetime5._tyserver._entity import ftglobal
from tuyoo5.core import tyglobal,typlugin
from tuyoo5.core.tyconfig import TyCachedConfig
from chengyudgr.entity.dao import UserDaoGameData, DaoRank, DaoRankInfo, mixDaoGameData, DaoWordContact
from chengyudgr.rank.rank import Rank
from chengyudgr.tencent.wx import upload_image, send_contact_msg
import time

SINGLE_GS_INDEX = 20312000000

class ChengyudgrPluginSrvJobs(typlugin.TYPlugin):

    def __init__(self):
        super(ChengyudgrPluginSrvJobs, self).__init__()
        self.jobs = []

    def destoryPlugin(self):
        DaoRank.finalize()
        DaoRankInfo.finalize()
        UserDaoGameData.finalize()
        mixDaoGameData.finalize()
        DaoWordContact.finalize()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_GAME_SINGLETON])
    def initPluginBefore(self):
        DaoRank.initialize()
        DaoRankInfo.initialize()
        UserDaoGameData.initialize()
        mixDaoGameData.initialize()
        DaoWordContact.initialize()


    def processUpdateRankInfo(self):
        """
        定时刷新排行帮数据
        @return:
        """
        ftlog.debug("ChengyudgrPluginSrvJobs processUpdateRankInfo")
        Rank.updata_rank()

    def resetRank(self, job):
        """
        重置排行榜
        """
        if job['type'] == "resetRank":
            now_time_str = time.strftime("%H:%M:%S")
            if now_time_str == job['triggertime']:
                ftlog.debug("ChengyudgrPluginSrvJobs processUpdateRankInfo")
                Rank.resetRank(job['rank_type'])

    def send_wx_contact(self, job, server_index):
        """
        发送客服消息
        @return:
        """
        if job['type'] == "send_wx_contact":
            now_time_str = time.strftime("%H:%M:%S")
            if now_time_str == job['triggertime']:
                ftlog.debug("ChengyudgrPluginSrvJobs send_wx_contact")
                if SINGLE_GS_INDEX == int(ftglobal.serverIdx):
                    upload_image()
                send_contact_msg(server_index)

    @typlugin.markPluginEntry(initAfterConfig=[tyglobal.SRV_TYPE_GAME_SINGLETON])
    def initPluginAfter(self):
        """
        初始化任务
        @return:
        """
        ftcore.runLoopSync(1, self.process)
        if SINGLE_GS_INDEX == int(ftglobal.serverIdx):
            ftcore.runLoopSync(600, self.processUpdateRankInfo)


    def process(self):
        """
        定时任务
        @return:
        """
        self.jobs = TyCachedConfig('jobs', tyglobal.gameId()).getScConfig() or []
        for job in self.jobs:
            # 重置排行榜
            if SINGLE_GS_INDEX == int(ftglobal.serverIdx):
                self.resetRank(job)
            # 发送客服消息
            self.send_wx_contact(job, (int(ftglobal.serverIdx)-SINGLE_GS_INDEX))

