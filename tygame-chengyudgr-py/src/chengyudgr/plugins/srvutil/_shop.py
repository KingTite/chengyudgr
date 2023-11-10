# -*- coding=utf-8  -*-

from freetime5.util import ftlog
from tuyoo5.core.tyconfig import TyCachedConfig
from tuyoo5.game import tybireport
from tuyoo5.core import tyglobal, typlugin
from freetime5.twisted.ftlock import lockargname
from chengyudgr.entity.dao import UserDaoGameData
from chengyudgr import util
from datetime import datetime, timedelta
import time

_DEBUG, debug = ftlog.getDebugControl(__name__)

# 判断是否免广告接口
def is_ad_remove(productId):
    """
    获取单个商品信息
    """
    shop_cof = TyCachedConfig('shop', tyglobal.gameId()).getScConfig() or []
    for val in shop_cof:
        if val['productId'] == productId:
            if val['ad_remove'] == 1:
                return True
            else:
                return False
    return False

# 获取商品信息
def get_product_info(productId):
    """
    获取单个商品信息
    """
    shop_cof = TyCachedConfig('shop', tyglobal.gameId()).getScConfig() or []
    for val in shop_cof:
        if val['productId'] == productId:
            return val
    return None

# 遍历支付记录，获取单个充值记录
def get_one_record_info(userId, orderId):
    """
    获取单个充值记录
    """
    db_record = UserDaoGameData.get_pay_record(userId) or []
    for val in db_record:
        if val['orderId'] == orderId:
            return val
    return None


# 遍历支付记录，获取是否买过某商品
def get_pay_count(userId, productId):
    """
    获取购买某个商品次数
    """
    db_record = UserDaoGameData.get_pay_record(userId) or []
    pay_count = 0
    for val in db_record:
        if val['prodId'] == productId:
            pay_count += 1
    return pay_count


# 遍历支付记录，获取购买某商品的最近时间
def get_pay_last_time(userId, productId):
    """
    获取购买某个商品次数
    """
    db_record = UserDaoGameData.get_pay_record(userId) or []
    last_time = 0
    for val in db_record:
        if val['prodId'] == productId:
            last_time = max(last_time, val['time'])
    return last_time

# 获取充值金额
def get_all_pay_money(userId):
    """
    获取用户全部充值金额
    """
    db_record = UserDaoGameData.get_pay_record(userId) or []
    money = 0
    for val in db_record:
        price = val.get("prodPrice", 0)
        money += price

    if _DEBUG:
        debug('_shop get_all_pay_money out ->', userId, money)
    return money


# sdk支付成功回调
@lockargname("_shop", "userId")
def sdk_pay_success(userId, sdk_param):
    """
    sdk支付成功接口
    @return:
    """
    ftlog.info('_shop sdk_pay_success in ->', userId, sdk_param)

    db_record_list = UserDaoGameData.get_pay_record(userId) or []
    db_record_info = get_one_record_info(userId, sdk_param['orderId'])
    if not db_record_info:
        # 免广告商品判断
        if is_ad_remove(sdk_param['prodId']):
            UserDaoGameData.set_ad_remove(userId, 1)
        sdk_param['complete'] = False
        sdk_param['time'] = int(time.time())
        db_record_list.append(sdk_param)
        UserDaoGameData.set_pay_record(userId, db_record_list)
    # 支付打点
    product_info = get_product_info(sdk_param['prodId'])
    if product_info:
        tybireport.reportGameEvent('CHENGYUDGR_SDK_PAY_SUCCESS',
                                   userId,
                                   tyglobal.gameId(),
                                   0, 0, 0, 0,
                                   0, int(product_info['id']),
                                   [],
                                   util.getClientId())
    return {"code": 0}

# 前端发货通知
@lockargname("_shop", "userId")
def order_complete(userId, order_info):
    """
    前端通知发货完成
    """
    ftlog.info('_shop order_complete in ->', userId, order_info)
    db_record_list = UserDaoGameData.get_pay_record(userId) or []
    for index, record in enumerate(db_record_list):
        if record['orderId'] == order_info['orderId']:
            db_record_list[index]['complete'] = True
            UserDaoGameData.set_pay_record(userId, db_record_list)
            return {"code": 0}
    if is_ad_remove(order_info['prodId']):
        UserDaoGameData.set_ad_remove(userId, 1)
    order_info['complete'] = True
    order_info['time'] = int(time.time())
    db_record_list.append(order_info)
    UserDaoGameData.set_pay_record(userId, db_record_list)
    return {"code": 0}


# 前端查询订单是否可发货
@lockargname("_shop", "userId")
def get_ready_order(userId, orderId):
    """
    前端查询订单是否可发货
    """
    ftlog.info('_shop get_ready_order in ->', userId, orderId)
    record_info = get_one_record_info(userId, orderId)
    # 订单不存在
    if not record_info:
        return {"code": 1}
    # 订单已经完成发货
    if record_info['complete']:
        return {"code": 2}
    # 返回待发货订单
    product_info = get_product_info(record_info['prodId'])
    record_info['product_info'] = product_info
    record_info['pay_count'] = get_pay_count(userId, record_info['prodId'])
    result = {
        "code": 0,
        "data": record_info
    }
    ftlog.debug('_shop get_ready_order out ->', userId, result)
    return result


# 登录查询全部补单
@lockargname("_shop", "userId")
def replacement_order(userId):
    """
    用户登录时返回补单信息
    @param userId:
    @return:
    """
    db_record_list = UserDaoGameData.get_pay_record(userId) or []
    replacement_order_list = []
    for index, val in enumerate(db_record_list):
        if not val['complete']:
            # 返回订单对应的商品信息
            product_info = get_product_info(val['prodId'])
            val['product_info'] = product_info
            val['pay_count'] = get_pay_count(userId, val['prodId'])
            replacement_order_list.append(val)
    if len(replacement_order_list) > 0:
        ftlog.info('_shop replacement_order in ->', userId, replacement_order_list)
    return replacement_order_list

@lockargname("_shop", "userId")
def get_product_list(userId, shopVersion):
    """
    获取可买商品列表
    """
    shop_cof = TyCachedConfig('shop', tyglobal.gameId()).getScConfig() or []
    can_show_list = []
    for val in shop_cof:
        # 不显示商品
        if not val.get('is_show'):
            continue
        # 当前版本显示的商品
        if isinstance(val['version'], list) and (shopVersion not in val['version']):
            continue
        if (isinstance(val['version'], str) or isinstance(val['version'], unicode)) and (shopVersion != val['version']):
            continue
        # 一次性消费商品
        pay_count = get_pay_count(userId, val['productId']) or 0
        if val['type'] == 2 and pay_count > 0:
            continue
        # 政绩活动限时月卡
        if val['type'] == 4:
            last_time = get_pay_last_time(userId, val['productId'])
            last_time_bejing = datetime.utcfromtimestamp(last_time) + timedelta(hours=8)  # 北京时间
            now_bejing = datetime.utcfromtimestamp(time.time()) + timedelta(hours=8)  # 北京时间
            if (last_time_bejing.month == now_bejing.month) and (last_time_bejing.year == now_bejing.year):
                continue
        can_show_d = {}
        can_show_d.update(val)
        can_show_d['pay_count'] = pay_count
        can_show_list.append(can_show_d)

    if _DEBUG:
        debug('_shop get_product_list', userId, can_show_list)

    if len(can_show_list) < 1:
        return {"code": 1}

    result = {
        "code": 0,
        "data": can_show_list
    }
    return result




