# -*- coding: utf-8 -*-

from freetime5.util import ftlog, ftstr, fttime
from tuyoo5.game import tybireport
from tuyoo5.core import tyrpcsdk, tyconfig, tyglobal, typlugin, tychecker
from tuyoo5.core.typlugin import pluginCross, gameRpcUtilOne
from chengyudgr.entity.dao import UserDaoGameData, mixDaoGameData, DaoRank, DaoRankInfo, DaoWordContact
from chengyudgr import util
from chengyudgr.tencent import wx
from . import _checker, _control_activity, game_logic
import time

_DEBUG, debug = ftlog.getDebugControl(__name__)

class ChengyudgrPluginSrvHttp(typlugin.TYPlugin):

    def __init__(self):
        super(ChengyudgrPluginSrvHttp, self).__init__()

        self.checker = tychecker.Checkers(
            _checker.check_userId,
            _checker.check_clientId
        )

        self.checkerUpdateBaseUserData = tychecker.Checkers(
            _checker.check_userId,
            _checker.check_name,
            _checker.check_icon
        )

        self.checkerOneUpdateBaseGameData = tychecker.Checkers(
                _checker.check_userId,
                _checker.check_clientId,
                _checker.check_questionId,
                _checker.check_dataKey,
                _checker.check_dataVal,
                _checker.check_isItem
        )

        self.checkerUpdateBaseData = tychecker.Checkers(
                _checker.check_userId,
                _checker.check_clientId,
                _checker.check_base_geme_data
        )

        self.checkerComment = tychecker.Checkers(
                _checker.check_userId,
                _checker.check_comment,
        )

        self.checkerMrjm = tychecker.Checkers(
                _checker.check_userId,
                _checker.check_state,
                _checker.check_flower,
                _checker.check_allTime,
        )

        self.checkerRankInfo = tychecker.Checkers(
                _checker.check_userId,
                _checker.check_rankName
        )

        self.checkerUpdateKejvData = tychecker.Checkers(
                _checker.check_userId,
                _checker.check_clientId,
                _checker.check_kejvData
        )

        self.checkerUpdateHardData = tychecker.Checkers(
                _checker.check_userId,
                _checker.check_clientId,
                _checker.check_hardData
        )

        self.checkerLogin = tychecker.Checkers(
                _checker.check_userId,
                _checker.check_clientId,
                _checker.check_version
        )

        self.checkerOrderComplete = tychecker.Checkers(
                _checker.check_userId,
                _checker.check_clientId,
                _checker.check_orderId,
                _checker.check_prodId,
                _checker.check_prodPrice,
                _checker.check_prodCount
        )

        self.checkerReadyOrder = tychecker.Checkers(
                _checker.check_userId,
                _checker.check_clientId,
                _checker.check_orderId
        )

        self.checkerProductList = tychecker.Checkers(
                _checker.check_userId,
                _checker.check_shopVersion
        )

        self.checkerCollect = tychecker.Checkers(
                _checker.check_userId,
                _checker.check_collectList
        )

    def destoryPlugin(self):
        UserDaoGameData.finalize()
        mixDaoGameData.finalize()
        DaoRank.finalize()
        DaoRankInfo.finalize()
        DaoWordContact.finalize()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_GAME_HTTP])
    def initPluginBefore(self):
        UserDaoGameData.initialize()
        mixDaoGameData.initialize()
        DaoRank.initialize()
        DaoRankInfo.initialize()
        DaoWordContact.initialize()

    @typlugin.markPluginEntry(initAfterConfig=[tyglobal.SRV_TYPE_GAME_HTTP])
    def initPluginAfter(self):
        pass

    @typlugin.markPluginEntry(httppath='get_game_data')
    def do_get_game_data(self, request):
        """
        自用
        """
        mi = self.checker.check(request)
        if mi.error:
            mo = {
                'code': 11,
                'info': str(mi.error)
            }
        else:
            try:
                mo = gameRpcUtilOne.srvutil.getGameDataInfo(mi.userId).getResult()
            except:
                ftlog.error()
                mo = {
                    'code': 10,
                }
        return mo


    @typlugin.markPluginEntry(httppath='update_base_game_data')
    def do_update_base_game_data(self, request):
        """
        更新玩家基础游戏数据
        @param request:
        @return:
        """

        ftlog.debug("ChengyudgrPluginSrvHttp do_update_base_game_data in")

        mi = self.checkerUpdateBaseData.check(request)

        if mi.error:
            mo = {
                'code': 11,
                'info': str(mi.error)
            }
        else:
            try:
                mo = gameRpcUtilOne.srvutil.updateBaseGameData(mi.userId, mi.base_geme_data).getResult()
            except:
                ftlog.error()
                mo = {
                    'code': 10,
                }
        return mo

    @typlugin.markPluginEntry(httppath='get_base_game_data')
    def do_get_base_game_data(self, request):
        """
        获取玩家基础游戏数据
        @param request:
        @return:
        """
        ftlog.debug("ChengyudgrPluginSrvHttp do_get_base_game_data in", request)

        mi = self.checker.check(request)

        if mi.error:
            mo = {
                'code': 11,
                'info': str(mi.error)
            }
        else:
            try:
                mo = gameRpcUtilOne.srvutil.getBaseGameData(mi.userId).getResult()
            except:
                ftlog.error()
                mo = {
                    'code': 10,
                }

        return mo

    @typlugin.markPluginEntry(httppath='updata_one_game_data')
    def do_updata_one_base_game_data(self, request):
        """
        更新玩家单个基础游戏数据
        @param request:
        @return:
        """
        ftlog.debug("ChengyudgrPluginSrvHttp do_updata_one_base_game_data in", request)

        mi = self.checkerOneUpdateBaseGameData.check(request)

        if mi.error:
            mo = {
                'code': 11,
                'info': str(mi.error)
            }
        else:
            try:
                mo = gameRpcUtilOne.srvutil.updataOneBaseGameData(mi.userId, mi.questionId, mi.dataKey, mi.dataVal, mi.isItem).getResult()
            except:
                ftlog.error()
                mo = {
                    'code': 10,
                }

        return mo


    @typlugin.markPluginEntry(httppath='add_comment')
    def comment(self, request):
        '''
        用户评论
        '''

        request.setHeader("Access-Control-Allow-Origin", "*")
        request.setHeader("Access-Control-Allow-Credentials", "true")
        request.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        request.setHeader('Access-Control-Allow-Headers', 'Content-Type,*')

        ftlog.info("ChengyudgrPluginSrvHttp doComment in")
        mi = self.checkerComment.check(request)
        if mi.error:
            mo = {
                'code': 11,
                'info': str(mi.error)
            }
        else:
            try:
                mo = gameRpcUtilOne.srvutil.doComment(mi.userId, mi.comment).getResult()

            except:
                ftlog.error()
                mo = {
                    'code': 10,
                }
        return mo

    @typlugin.markPluginEntry(httppath='get_comments')
    def doGetComments(self, request):
        '''
        获取用户全部评论（test自用）
        '''
        userId = request.getParamInt('userId')
        try:
            mo = gameRpcUtilOne.srvutil.getComments(userId).getResult()
        except:
            ftlog.error()
            mo = {
                'code': 10,
            }
        return mo

    @typlugin.markPluginEntry(httppath='update_mrjm')
    def doUpdateMrjm(self, request):
        '''
        上传每日解谜活动信息
        '''
        ftlog.info("ChengyudgrPluginSrvHttp doUpdateMrjm in")
        mi = self.checkerMrjm.check(request)
        if mi.error:
            mo = {
                'code': 11,
                'info': str(mi.error)
            }
        else:
            try:
                mo = gameRpcUtilOne.srvutil.updateMrjm(mi.userId, mi.state, mi.flower, mi.allTime).getResult()

            except:
                ftlog.error()
                mo = {
                    'code': 10,
                }
        return mo

    @typlugin.markPluginEntry(httppath='get_rank_info')
    def dogetRankInfo(self, request):
        '''
        获取排行榜详情
        '''
        ftlog.info("ChengyudgrPluginSrvHttp dogetRankInfo in")
        mi = self.checkerRankInfo.check(request)
        if mi.error:
            mo = {
                'code': 11,
                'info': str(mi.error)
            }
        else:
            try:
                mo = gameRpcUtilOne.srvutil.getRankInfo(mi.userId, mi.rankName).getResult()
            except:
                ftlog.error()
                mo = {
                    'code': 10,
                }
        return mo

    @typlugin.markPluginEntry(httppath='update_kejv_data')
    def doUpdateKejvData(self, request):
        '''
        上传科举数据
        '''
        ftlog.info("ChengyudgrPluginSrvHttp doUpdateKejv in")
        mi = self.checkerUpdateKejvData.check(request)
        if mi.error:
            mo = {
                'code': 11,
                'info': str(mi.error)
            }
        else:
            try:
                mo = gameRpcUtilOne.srvutil.updateKejvData(mi.userId, mi.kejvData).getResult()
            except:
                ftlog.error()
                mo = {
                    'code': 10,
                }
        return mo

    @typlugin.markPluginEntry(httppath='get_kejv_data')
    def doGetKejvData(self, request):
        '''
        获取科举数据
        '''
        ftlog.info("ChengyudgrPluginSrvHttp doGetKejvData in")
        mi = self.checker.check(request)
        if mi.error:
            mo = {
                'code': 11,
                'info': str(mi.error)
            }
        else:
            try:
                mo = gameRpcUtilOne.srvutil.geteKejvData(mi.userId).getResult()

            except:
                ftlog.error()
                mo = {
                    'code': 10,
                }
        return mo

    @typlugin.markPluginEntry(httppath='update_hard_data')
    def doUpdateHardData(self, request):
        '''
        上传极限玩法数据
        '''
        ftlog.info("ChengyudgrPluginSrvHttp doUpdateHardData in")
        mi = self.checkerUpdateHardData.check(request)
        if mi.error:
            mo = {
                'code': 11,
                'info': str(mi.error)
            }
        else:
            try:
                mo = gameRpcUtilOne.srvutil.updateHardData(mi.userId, mi.hardData).getResult()

            except:
                ftlog.error()
                mo = {
                    'code': 10,
                }
        return mo

    @typlugin.markPluginEntry(httppath='get_hard_data')
    def doGetHardData(self, request):
        '''
        获取极限玩法数据
        '''
        ftlog.info("ChengyudgrPluginSrvHttp doGetHardData in")
        mi = self.checker.check(request)
        if mi.error:
            mo = {
                'code': 11,
                'info': str(mi.error)
            }
        else:
            try:
                mo = gameRpcUtilOne.srvutil.geteHardData(mi.userId).getResult()

            except:
                ftlog.error()
                mo = {
                    'code': 10,
                }
        return mo

    @typlugin.markPluginEntry(httppath='get_control_activity')
    def doGetControlActivity(self, request):
        '''
        获取活动控制表(产品需求不登录也能获取)
        '''
        ftlog.info("ChengyudgrPluginSrvHttp doGetControlActivity in")
        params = _checker.getParams(request) or {}
        activity_id = params.get('activity_id')
        try:
            result_data = _control_activity.get_all_activity_data(activity_id)
            mo = {
                'code': 0,
                'data': result_data
            }
        except:
            ftlog.error()
            mo = {
                'code': 10,
            }
        return mo

    @typlugin.markPluginEntry(httppath='set_activity')
    def doSetActivity(self, request):
        '''
        设置活动时间（自用）
        '''
        params = _checker.getParams(request)
        ftlog.info("ChengyudgrPluginSrvHttp doSetActivity in")
        try:
            activityId = params.get('activityId', 0)
            activity_info = params.get('activity_info', {})
            _control_activity.set_activity_info(activityId, activity_info)
            mo = {
                'code': 0
            }
        except:
            ftlog.error()
            mo = {
                'code': 10,
            }
        return mo


    @typlugin.markPluginEntry(httppath='login')
    def doLogin(self, request):
        '''
        登录
        '''
        params = _checker.getParams(request)
        ftlog.info("ChengyudgrPluginSrvHttp login in params -> ", params)
        mi = self.checkerLogin.check(request)
        if mi.error:
            mo = {
                'code': 11,
                'info': str(mi.error)
            }
        else:
            try:
                # 构造登录参数数据
                login_param = {
                    'clientId': mi.clientId,
                    'version': mi.version,
                    'name': params.get('name'),
                    'icon': params.get('icon'),
                    'is_wx': params.get('is_wx', False),
                    'game_type': params.get('game_type')
                }
                mo = gameRpcUtilOne.srvutil.longin(mi.userId, login_param).getResult()
                ftlog.debug("ChengyudgrPluginSrvHttp login out mo", mi.userId, mo)
            except:
                ftlog.error()
                mo = {
                    'code': 10,
                }
        return mo

    @typlugin.markPluginEntry(httppath='sdk_pay_success')
    def doSdkPaySuccess(self, request):
        """
        sdk支付成功回调
        """
        ftlog.info("ChengyudgrPluginSrvHttp doSdkPaySuccess request -> ", request)
        clientId = request.getParamStr('clientId') or util.getClientId()
        userId = request.getParamInt('userId')

        tybireport.reportGameEvent('CHENGYUDGR_SDK_PAY_NOTICE', request.getParamInt('userId'), tyglobal.gameId(), 0, 0, 0, 0, 0, 0, [], clientId)

        if not userId:
            return
        if not request.getParamStr('platformOrder'):
            return
        if not request.getParamStr('prodId'):
            return
        if not request.getParamFloat('prodPrice'):
            return

        sdk_param = {}
        sdk_param['userId'] = request.getParamInt('userId')
        sdk_param['orderId'] = request.getParamStr('platformOrder')
        sdk_param['prodId'] = request.getParamStr('prodId')
        sdk_param['prodPrice'] = request.getParamFloat('prodPrice')
        sdk_param['prodCount'] = request.getParamStr('prodCount')

        try:
            gameRpcUtilOne.srvutil.sdkPaySuccess(userId, sdk_param)
        except:
            ftlog.error()

        if _DEBUG:
            debug("ChengyudgrPluginSrvHttp doSdkPaySuccess out success ")

        return 'success'


    @typlugin.markPluginEntry(httppath='get_ready_orderd')
    def doGetReadyOrder(self, request):
        '''
        前端请求待发货订单
        '''
        ftlog.info("ChengyudgrPluginSrvHttp doGetReadyOrder in")
        mi = self.checkerReadyOrder.check(request)
        if mi.error:
            mo = {
                'code': 11,
                'info': str(mi.error)
            }
        else:
            try:
                mo = gameRpcUtilOne.srvutil.getReadyOrder(mi.userId, mi.orderId).getResult()
            except:
                ftlog.error()
                mo = {
                    'code': 10,
                }
        if _DEBUG:
            debug("ChengyudgrPluginSrvHttp doGetReadyOrder out ->", mo)
        return mo

    @typlugin.markPluginEntry(httppath='order_complete')
    def doOrderComplete(self, request):
        '''
        前端发货成功
        '''
        ftlog.info("ChengyudgrPluginSrvHttp doOrderComplete in")
        mi = self.checkerOrderComplete.check(request)
        if mi.error:
            mo = {
                'code': 11,
                'info': str(mi.error)
            }
        else:
            try:
                order_info = {}
                order_info['userId'] = mi.userId
                order_info['orderId'] = mi.orderId
                order_info['prodId'] = mi.prodId
                order_info['prodPrice'] = mi.prodPrice
                order_info['prodCount'] = mi.prodCount
                mo = gameRpcUtilOne.srvutil.orderComplete(mi.userId, order_info).getResult()
            except:
                ftlog.error()
                mo = {
                    'code': 10,
                }

        if _DEBUG:
            debug("ChengyudgrPluginSrvHttp doOrderComplete out ->", mo)

        return mo

    @typlugin.markPluginEntry(httppath='get_product_list')
    def doGetProductList(self, request):
        '''
        获取商品列表
        '''
        ftlog.info("ChengyudgrPluginSrvHttp doGetProductList in")
        mi = self.checkerProductList.check(request)
        if mi.error:
            mo = {
                'code': 11,
                'info': str(mi.error)
            }
        else:
            try:
                mo = gameRpcUtilOne.srvutil.getProductList(mi.userId, mi.shopVersion).getResult()
            except:
                ftlog.error()
                mo = {
                    'code': 10,
                }

        if _DEBUG:
            debug("ChengyudgrPluginSrvHttp doGetProductList out ->", mo)

        return mo


    @typlugin.markPluginEntry(httppath='check/config')
    def doCheckConfig(self, request):
        '''
        检查md5，并进行更新
        :param request:
        :return:
        '''
        params = _checker.getParams(request)
        if not params:
            return {}
        if ftlog.is_debug():
            ftlog.debug('doCheckConfig',
                        'params=', params)
        return game_logic.CheckMD5ReturnNewconfig(params)

    @typlugin.markPluginEntry(httppath='update_collect_idiomId')
    def doUpdateCollectIdiomId(self, request):
        """
        更新收藏的成语
        @param request:
        @return:
        """
        ftlog.info("ChengyudgrPluginSrvHttp doUpdateCollectIdiomId in")
        mi = self.checkerCollect.check(request)
        if mi.error:
            mo = {
                'code': 11,
                'info': str(mi.error)
            }
        else:
            try:
                mo = gameRpcUtilOne.srvutil.updateCollectIdiomId(mi.userId, mi.collectList).getResult()
            except:
                ftlog.error()
                mo = {
                    'code': 10,
                }

        if _DEBUG:
            debug("ChengyudgrPluginSrvHttp doUpdateCollectIdiomId out ->", mo)
        return mo

    @typlugin.markPluginEntry(httppath='get_collect_idiomId')
    def doGetCollectIdiomId(self, request):
        """
        获取收藏的成语
        @param request:
        @return:
        """
        ftlog.info("ChengyudgrPluginSrvHttp getCollectIdiomId in")
        mi = self.checker.check(request)
        if mi.error:
            mo = {
                'code': 11,
                'info': str(mi.error)
            }
        else:
            try:
                mo = gameRpcUtilOne.srvutil.getCollectIdiomId(mi.userId).getResult()
            except:
                mo = {
                    'code': 10,
                }
        if _DEBUG:
            debug("ChengyudgrPluginSrvHttp getCollectIdiomId out ->", mo)
        return mo

    @typlugin.markPluginEntry(httppath='get_wx_access_token')
    def doGetWxAccessToken(self, request):
        """
        测试服使用线上的token，保证只有一个中控机
        """
        return wx.get_wx_access_token()

    @typlugin.markPluginEntry(httppath='wx_contact')
    def doWxContact(self, request):
        """
        微信客服消息
        @param request:
        @return:
        """
        body = request.getBody()
        body_params = ftstr.loads(body, ignoreException=True, execptionValue={})
        params = request.getDict()
        params.update(body_params)
        ftlog.info('ChengyudgrPluginSrvHttp doWxContact in ->', params)
        return wx.answer(params)

    @typlugin.markPluginEntry(httppath='get_wx_contact_media')
    def doGetWxContactMedia(self, request):
        """
        获取当前素材id详情（自用）
        """
        db_media = mixDaoGameData.get_wx_media()
        return db_media

    @typlugin.markPluginEntry(httppath='set_wx_contact_media')
    def doSetWxContactMedia(self, request):
        """
        设置当前素材id详情（自用）
        {
          "image_1": {
            "created_at": 1569229863,
            "media_id": "yyCCI7yowSBbGh8cx5tNZnFTxFCc3Fkrwfj5ks5E8jsTaEA13acCXTuvFM9N89mC"
          },
          "image_2": {
            "created_at": 1569229875,
            "media_id": "PGmdTfjKp3kP1FBrwy1xCTMfwPLPbkqb0e79TOKjt8ytVTPhf-iSDo3MKlC_CYGd"
          },
          "image_3": {
            "created_at": 1569229877,
            "media_id": "d17xtNT_5u3hlHezjOJAHnkpGY6QaliN-LJxCA0oKhlUMwnv-JuTkBAEzkZourrB"
          }
        }
        """
        params = _checker.getParams(request)
        ftlog.info("ChengyudgrPluginSrvHttp setWxContactMedia in")
        try:
            mediaData = params.get('mediaData', {})
            mixDaoGameData.set_wx_media(mediaData)
            mo = {
                'code': 0
            }
        except:
            ftlog.error()
            mo = {
                'code': 10,
            }
        return mo

    @typlugin.markPluginEntry(httppath='reward_wx_contact')
    def doRewardWxContact(self, request):
        """
        进入客服领体力
        """
        params = _checker.getParams(request)
        ftlog.info("ChengyudgrPluginSrvHttp setWxContactMedia in")
        try:
            if not params.get('openId'):
                mo = {
                    'code': 11,
                }
            else:
                db_data = DaoWordContact.getOneOpenId(params['openId']) or {}
                is_miniprogrampage_today = fttime.is_same_day(db_data.get('miniprogrampage', 0), time.time())
                if not is_miniprogrampage_today:
                    # 不能领
                    mo = {'code': 1}
                else:
                    is_reward_today = fttime.is_same_day(db_data.get('reward', 0), time.time())
                    # 领取过了了
                    if is_reward_today:
                        mo = {'code': 2}
                    else:
                        DaoWordContact.updateOneOpenId(params['openId'], "reward", int(time.time()))
                        mo = {'code': 0}
        except:
            ftlog.error()
            mo = {
                'code': 10,
            }
        return mo

    @typlugin.markPluginEntry(httppath='qq_update_formId')
    def doQqUpdateFormId(self, request):
        """
        qq上传formId,用于发送模板消息（暂未开通）
        @param request:
        @return:
        """
        # body = request.getBody()
        # params = ftstr.loads(body, ignoreException=True, execptionValue={})
        # ftlog.info('ChengyudgrPluginSrvHttp doQqUpdateFormId in ->', params)
        return "success"




