# -*- coding: utf-8 -*-

from freetime5.util import ftlog
from tuyoo5.core.tyconfig import TyCachedConfig
from tuyoo5.core import tyrpcsdk
from tuyoo5.core import tyglobal

from chengyudgr.entity.dao import UserDaoGameData, DaoRank, DaoRankInfo


class Rank(object):
    '''
    排行榜
    '''

    @classmethod
    def _get_rank(cls, rank_name):
        '''
        获取排行榜
        '''
        rank_list = []

        cfg_rank = TyCachedConfig('rank', tyglobal.gameId()).getScConfig()
        if not cfg_rank.get(rank_name):
            return rank_list

        rank_db = DaoRank.get_rank_with_score_list(rank_name, cfg_rank[rank_name]['asc_order'], cfg_rank[rank_name]['rank_max'])

        if rank_db:
            rank_list = [rank_db[i:i + 2] for i in range(0, len(rank_db), 2)]  # 列表两两切分成 member:score

        if ftlog.is_debug():
            ftlog.debug('Rank _getNewRankList result->', rank_list)

        return rank_list

    @classmethod
    def add_score_to_rank(cls, rank_name, userId, score):
        '''
        score插入排行榜
        '''
        # 是否有昵称和头像
        user_data = UserDaoGameData.get_base_user_data(userId) or {}
        if not score or score <= 0:
            return
        if not user_data.get('is_wx') or not user_data.get('icon'):
            return
        # 排行榜名称判断
        cfg_rank = TyCachedConfig('rank', tyglobal.gameId()).getScConfig()
        if not cfg_rank.get(rank_name):
            return

        if ftlog.is_debug():
            ftlog.debug('Rank add_score_to_rank', rank_name, userId, score)
        DaoRank.add_rank_score(rank_name, userId, score, cfg_rank[rank_name]['asc_order'], cfg_rank[rank_name]['rank_max'])

        # 总榜分开（手q 和其他）
        game_type = user_data.get('game_type')
        if game_type:
            other_rank_name = str(game_type) + '_' + rank_name
            if cfg_rank.get(other_rank_name):
                DaoRank.add_rank_score(other_rank_name, userId, score, cfg_rank[other_rank_name]['asc_order'], cfg_rank[other_rank_name]['rank_max'])

    @classmethod
    def resetRank(cls, rank_type):
        """
        重置排行榜
        """
        cnf_rank = TyCachedConfig('rank', tyglobal.gameId()).getScConfig()
        for key, val in cnf_rank.items():
            if val['type'] == rank_type:
                DaoRank.reset_rank(val['rank_name'])
                DaoRankInfo.set_rank_info_data(val['rank_name'], [])
                ftlog.debug('Rank resetRank', val['rank_name'], rank_type)

    @classmethod
    def updata_rank(cls):
        """
        更新排行榜详情(用于用户获取)
        @return:
        """
        # 获取全部排行榜配置
        cfg_rank = TyCachedConfig('rank', tyglobal.gameId()).getScConfig()
        for key, val in cfg_rank.items():
            # 获取排行榜列表
            rank_list = cls._get_rank(val['rank_name'])
            rank_info_list = []
            # 格式化排行榜要显示的全部信息
            for rankid, rankInfo in enumerate(rank_list):
                userId = rankInfo[0]
                score = rankInfo[1]
                tyrpcsdk.checkUserData(userId)  # 热转冷后的数据需要
                baseGameData = {
                    "OfficialLevel": UserDaoGameData.get_base_game_data_by_key(userId, "OfficialLevel")
                }
                _d = {
                    "userId": userId,
                    "ranking": rankid,
                    "rankVal": score,
                    "baseGameData": baseGameData,
                    "mrjm_flower": UserDaoGameData.get_mrjm_flower(userId),
                    "userInfo": UserDaoGameData.get_base_user_data(userId)
                }
                rank_info_list.append(_d)
            DaoRankInfo.set_rank_info_data(val['rank_name'], rank_info_list)

    @classmethod
    def get_rank_info(cls, userId, rank_name):
        '''
        用户获取排行榜详情信息
        '''
        cfg_rank = TyCachedConfig('rank', tyglobal.gameId()).getScConfig()
        if rank_name not in cfg_rank:
            return {'code': 1}
        rank_num = cfg_rank[rank_name]["rank_num"]
        db_rank_info_list = DaoRankInfo.get_rank_info_data(rank_name)
        user_rank = -1
        user_rankVal = -1
        # 排行榜数量不足
        # if rank_num > len(db_rank_info_list):
        #     return {'code': 2}

        for val in db_rank_info_list:
            if int(val['userId']) == int(userId):
                user_rank = val['ranking']
                user_rankVal = val['rankVal']

        result = {
            "rank_info": {
                'user_rank': user_rank,
                'user_rankVal': user_rankVal,
                'rank_info_list': db_rank_info_list[0:rank_num]
            },
            'code': 0
        }
        if ftlog.is_debug():
            ftlog.debug('Rank get_rank_info result->', result)

        return result
