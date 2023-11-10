# -*- coding: utf-8 -*-

import time
from freetime5.util import ftlog
from freetime5.util import fttime
from tuyoo5.core import tyglobal, tydao
from tuyoo5.core.tydao import DataAttrBoolean
from tuyoo5.core.tydao import DataAttrDateTime
from tuyoo5.core.tydao import DataAttrInt
from tuyoo5.core.tydao import DataAttrFloat
from tuyoo5.core.tydao import DataAttrIntAtomic
from tuyoo5.core.tydao import DataAttrObjList
from tuyoo5.core.tydao import DataAttrStr
from tuyoo5.core.tydao import attrsDefinedClass, DataAttrObjDict
from tuyoo5.core import tyrpcsdk, tyrpchall
from collections import deque, defaultdict


@attrsDefinedClass
class UserDaoKeys(object):
    # 用户基础信息
    ATT_BASE_GAME_DATA = DataAttrObjDict('base_game_data', {}, 1024)
    # 用户个人信息
    ATT_BASE_USER_DATA = DataAttrObjDict('base_user_data', {}, 1024)
    # 每日解谜活动获取鲜花数量
    ATT_MRJM_FLOWER = DataAttrInt('mrjm_flower', 0)
    # 科举信息
    ATT_KEJV = DataAttrObjDict('kejv', {}, 1024)
    # 极限玩法
    ATT_HARD = DataAttrObjDict('hard', {}, 1024)
    # 充值记录
    ATT_PAY_RECORD = DataAttrObjList('pay_record', [], 1024)
    # 免广告
    ATT_AD_REMOVE = DataAttrInt('ad_remove', 0)
    # 收藏成语Id
    ATT_COLLECT = DataAttrObjList('collect', [], 1024)
    # 最后更新数据时间
    ATT_UPDATE_TIME = DataAttrInt('update_time', 0)


class UserDaoGameData(tydao.DataSchemaHashAttrs):
    DBNAME = 'user'
    MAINKEY = 'gamedata:20312:%s' % ('%s')

    ATTS = UserDaoKeys


    @classmethod
    def getMainKey(cls, cIndex, mainKeyExt=None):
        return cls.MAINKEY % cIndex

    @classmethod
    def get_game_data(cls, userId):
        return cls.HGETALL(userId)

    @classmethod
    def set_base_game_data(cls, userId, data):
        cls.set_update_time(userId)
        cls.HSET(userId, UserDaoKeys.ATT_BASE_GAME_DATA, data)

    @classmethod
    def get_base_game_data(cls, userId):
        return cls.HGET(userId, UserDaoKeys.ATT_BASE_GAME_DATA)

    @classmethod
    def get_base_game_data_by_key(cls, userId, key):
        base_game_data = cls.HGET(userId, UserDaoKeys.ATT_BASE_GAME_DATA) or {}
        if key in base_game_data:
            return base_game_data[key]
        return None

    @classmethod
    def set_mrjm_flower(cls, userId, flower):
        cls.set_update_time(userId)
        cls.HSET(userId, UserDaoKeys.ATT_MRJM_FLOWER, flower)

    @classmethod
    def get_mrjm_flower(cls, userId):
        return cls.HGET(userId, UserDaoKeys.ATT_MRJM_FLOWER)

    @classmethod
    def set_base_user_data(cls, userId, data):
        cls.HSET(userId, UserDaoKeys.ATT_BASE_USER_DATA, data)

    @classmethod
    def get_base_user_data(cls, userId):
        return cls.HGET(userId, UserDaoKeys.ATT_BASE_USER_DATA)

    @classmethod
    def set_kejv_data(cls, userId, data):
        cls.set_update_time(userId)
        cls.HSET(userId, UserDaoKeys.ATT_KEJV, data)

    @classmethod
    def get_kejv_data(cls, userId):
        return cls.HGET(userId, UserDaoKeys.ATT_KEJV)

    @classmethod
    def set_hard_data(cls, userId, data):
        cls.set_update_time(userId)
        cls.HSET(userId, UserDaoKeys.ATT_HARD, data)

    @classmethod
    def get_hard_data(cls, userId):
        return cls.HGET(userId, UserDaoKeys.ATT_HARD)

    @classmethod
    def set_pay_record(cls, userId, data):
        cls.HSET(userId, UserDaoKeys.ATT_PAY_RECORD, data)

    @classmethod
    def get_pay_record(cls, userId):
        return cls.HGET(userId, UserDaoKeys.ATT_PAY_RECORD)

    @classmethod
    def set_ad_remove(cls, userId, ad_remove):
        cls.HSET(userId, UserDaoKeys.ATT_AD_REMOVE, ad_remove)

    @classmethod
    def get_ad_remove(cls, userId):
        return cls.HGET(userId, UserDaoKeys.ATT_AD_REMOVE)

    @classmethod
    def set_collect(cls, userId, collectList):
        cls.HSET(userId, UserDaoKeys.ATT_COLLECT, collectList)

    @classmethod
    def get_collect(cls, userId):
        return cls.HGET(userId, UserDaoKeys.ATT_COLLECT)

    @classmethod
    def set_update_time(cls, userId):
        cls.HSET(userId, UserDaoKeys.ATT_UPDATE_TIME, int(time.time()))

    @classmethod
    def get_update_time(cls, userId):
        return cls.HGET(userId, UserDaoKeys.ATT_UPDATE_TIME)


# mix库
@attrsDefinedClass
class MixDaoKeys(object):
    # 活动信息
    ATT_SEASON_DATA = DataAttrObjDict('season_data', {}, 1024)
    # 微信token
    ATT_WX_ACCESS_TOKEN = DataAttrObjDict('wx_access_token', {}, 1024)
    # wx 图片素材id
    ATT_WX_MEDIA = DataAttrObjDict('wx_media', {}, 1024)
    # qq token
    ATT_QQ_ACCESS_TOKEN = DataAttrObjDict('qq_access_token', {}, 1024)


class mixDaoGameData(tydao.DataSchemaHashAttrs):
    DBNAME = 'mix'
    MAINKEY = 'mixgamedata:20312:%s' % ('%s')

    ATTS = MixDaoKeys

    @classmethod
    def getMainKey(cls, cIndex, mainKeyExt=None):
        return cls.MAINKEY % cIndex

    @classmethod
    def set_season_data(cls, activity_id, data):
        cls.HSET(activity_id, MixDaoKeys.ATT_SEASON_DATA, data)

    @classmethod
    def get_season_data(cls, activity_id):
        return cls.HGET(activity_id, MixDaoKeys.ATT_SEASON_DATA)

    @classmethod
    def set_wx_access_token(cls, access_token_d):
        cls.HSET(0, MixDaoKeys.ATT_WX_ACCESS_TOKEN, access_token_d)

    @classmethod
    def get_wx_access_token(cls):
        return cls.HGET(0, MixDaoKeys.ATT_WX_ACCESS_TOKEN)

    @classmethod
    def set_wx_media(cls, media):
        cls.HSET(0, MixDaoKeys.ATT_WX_MEDIA, media)

    @classmethod
    def get_wx_media(cls):
        return cls.HGET(0, MixDaoKeys.ATT_WX_MEDIA)

    @classmethod
    def set_qq_access_token(cls, access_token_d):
        cls.HSET(0, MixDaoKeys.ATT_QQ_ACCESS_TOKEN, access_token_d)

    @classmethod
    def get_qq_access_token(cls):
        return cls.HGET(0, MixDaoKeys.ATT_QQ_ACCESS_TOKEN)

# 排行榜redis
class DaoRank(tydao.DataSchemaZset):
    """
    排行榜数据库的Redis存储实现.
    """
    DBNAME = 'rank'
    MAINKEY = 'rank:20312'
    SUBVALDEF = tydao.DataAttrObjDict('cydgr_rank', {}, 256)

    @classmethod
    def getMainKey(cls, cIndex, mainKeyExt=None):
        return cls.MAINKEY + ':' + str(mainKeyExt)

    @classmethod
    def add_rank_score(cls, rankName, userId, score, asc=False, rankMax=1000):
        """
        刷新排行榜
        asc: 升序：True 降序：False
        """
        if ftlog.is_debug():
            ftlog.debug('DaoRank addRank->', rankName, userId, score, asc)

        # 查询玩家是否已经在排行版
        existsScore = cls.ZSCORE(0, userId, mainKeyExt=rankName)
        if existsScore:
            if asc and existsScore < score:
                return
            if not asc and existsScore >= score:
                return

        # 插入排行数据
        cls.ZADD(0, score, userId, mainKeyExt=rankName)

        # 获取当前长度
        count = cls.ZCARD(0, mainKeyExt=rankName)

        # 超出最大长度，删除排行较低的用户
        if count >= rankMax:
            if not asc:
                cls.ZREMRANGEBYRANK(0, 0, -(rankMax + 1), mainKeyExt=rankName)
            else:
                cls.ZREMRANGEBYRANK(0, rankMax, rankMax + 1, mainKeyExt=rankName)

    @classmethod
    def get_rank_with_score_list(cls, rankName, asc=False, rank_num=100):
        """
        获取游戏排行版并且获取游戏排行的分数
        """
        if not asc:
            # 倒序, 分数最大的在前面，表示最新的记录
            result = cls.ZREVRANGE(0, 0, rank_num - 1, True, mainKeyExt=rankName) or []
        else:
            result = cls.ZRANGE(0, 0, rank_num - 1, True, mainKeyExt=rankName) or []

        if ftlog.is_debug():
            ftlog.debug('DaoRank getRankWithScoreList',
                        'rankName=', rankName,
                        'asc=', asc,
                        'result=', result)
        return result

    @classmethod
    def reset_rank(cls, rankName):
        """
        重置排行榜
        """
        if ftlog.is_debug():
            ftlog.debug('DaoRank resetRank->', rankName)
        # 获取当前长度
        cls.ZREMRANGEBYRANK(0, 0, -1, mainKeyExt=rankName)

    @classmethod
    def zscore_rank(cls, userId, rankName):
        """
        获取用户在排行榜上的分数
        """
        if ftlog.is_debug():
            ftlog.debug('DaoRank zscore_rank->', rankName, userId)
        # 获取当前玩家分数
        existsScore = cls.ZSCORE(0, userId, mainKeyExt=rankName) or 0
        return existsScore

    @classmethod
    def zrevrank_rank(cls, userId, rankName):
        """
        获取用户在排行榜上的名次
        """
        if ftlog.is_debug():
            ftlog.debug('DaoRank zrevrank_rank->', rankName, userId)
        # 获取当前玩家名次
        ranking = cls.ZREVRANK(0, userId, mainKeyExt=rankName)
        if ranking is None:
            ranking = -1
        return ranking


# 前端请求用的排行榜
class DaoRankInfo(tydao.DataSchemaHashSameKeys):
    """
    (用于客户端拉取)排行榜数据库的Redis存储实现.
    MAINKEY,数据键值
    """
    DBNAME = 'rank'
    MAINKEY = 'rankInfo:20312'
    SUBVALDEF = tydao.DataAttrObjList('cydgr_rank_info', [], 1024)

    @classmethod
    def getMainKey(cls, cIndex, mainKeyExt=None):
        return cls.MAINKEY

    @classmethod
    def set_rank_info_data(cls, rankName, rankList):
        """
        保存排行榜数据
        """
        if ftlog.is_debug():
            ftlog.debug('DaoRankInfo setRankInfo->', rankName, rankList)
        cls.HSET(0, rankName, rankList)

    @classmethod
    def get_rank_info_data(cls, rankName):
        """
        获取排行榜信息
        """
        result = cls.HGET(0, rankName)
        if ftlog.is_debug():
            ftlog.debug('DaoRankInfo getRankInfo result ->', rankName, result)
        return result


class DaoWordComment(tydao.MongoDbSchema):
    """
    用户评论
    """

    DBNAME = 'piccomment'
    COLLECTION_NAME = 'cydgr_comment'

    @classmethod
    def addComment(cls, userId, comment):
        """
        每个用户保存最后10条数据
        """
        db_data = cls.find(0, {'userId': userId})
        if len(db_data) >= 10:
            del_d = min(db_data, key=lambda d: d.get('inser_time', 0))
            cls.delete_one(0, del_d)
        data = {
            'userId': userId,
            'comment': comment,
            'inser_time': int(time.time())
        }
        result = cls.insert_one(0, data)
        return result

    @classmethod
    def getComments(cls):
        """
        获取全部评论
        """
        data = {
            'comments': cls.find(0)
        }
        return data


class DaoWordContact(tydao.MongoDbSchema):
    """
    联系客服的openId
    """

    DBNAME = 'piccomment'
    COLLECTION_NAME = 'cydgr_contact'

    @classmethod
    def addOpenId(cls, openId):
        """
        增加openId
        """
        db_data = cls.find(0, {'openId': openId})
        if len(db_data) > 0:
            result = cls.update_one(0, {'openId': openId},
                                    {
                                        "$set": {
                                            'lastContactTime': int(time.time())
                                        }
                                    }, )
        else:
            data = {
                'openId': openId,
                'lastContactTime': int(time.time())
            }
            result = cls.insert_one(0, data)
        return result

    @classmethod
    def delOpenId(cls, openId):
        """
        删除过期的openId
        """
        cls.delete_one(0, openId)

    @classmethod
    def getOneOpenId(cls, openId):
        """
        获取单个openId内容
        """
        data = cls.find_one(0, {'openId': openId})
        return data

    @classmethod
    def updateOneOpenId(cls, openId, key, val):
        """
        获取单个openId内容(时间戳、0、空)
        """
        data = cls.find_one(0, {'openId': openId})
        if data:
            cls.update_one(
                    0,
                    {'openId': openId},
                    {
                        "$set": {
                            key: val
                        }
                    },
            )
        return data

    @classmethod
    def getThousandOpenId(cls, index, limit=1000):
        """
        获取1000个openId对象
        """
        db_openIds = cls.find(0, skip=index*limit, limit=limit)
        ftlog.info('DaoWordContact getThousandOpenId ->', index, len(db_openIds))
        return db_openIds

class DaoWordTemplate(tydao.MongoDbSchema):
    """
    发送模板消息
    """

    DBNAME = 'piccomment'
    COLLECTION_NAME = 'cydgr_template'

    @classmethod
    def insertOne(cls, userId, openId, templetId):
        """
        增加openId
        """
        db_data = cls.find_one(0, {'userId': userId})
        if db_data:
            templateIds = db_data.get('templateIds', [])
            templateIds.append(templetId)
            result = cls.update_one(0, {'openId': openId},
                                    {
                                        "$set": {
                                            'lastContactTime': int(time.time()),
                                            'templateIds': templateIds
                                        }
                                    }, )
        else:
            data = {
                'userId': userId,
                'openId': openId,
                "templateIds": [templetId],
                'lastContactTime': int(time.time())
            }
            result = cls.insert_one(0, data)
        return result

    @classmethod
    def deleteOne(cls, one_data):
        """
        删除过期的openId
        """
        cls.delete_one(0, one_data)

    @classmethod
    def findOne(cls, userId, templetId):
        """
        获取单个openId内容
        """
        data = cls.find_one(0, {'userId': userId})
        if data:
            if templetId in data['templateIds']:
                return data
        return None

    @classmethod
    def getThousandData(cls, index, limit=1000):
        """
        获取1000个openId对象
        """
        db_openIds = cls.find(0, skip=index*limit, limit=limit)
        ftlog.info('DaoWordContact getThousandData ->', index, len(db_openIds))
        return db_openIds
