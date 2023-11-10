# -*- coding=utf-8  -*-


import json
import codecs
from collections import Counter
import random
import os
import math

"""
生成需求答案（根据提示字数目）
"""
# 提示类型
HINT_RANDOM = 1  # 提示字位置随机
HINT_CROSS = 2  # 提示优先交叉
HINT_No_CROSS = 3  # 提示字非交叉字
HINT_FIRST = 4  # 提示优先首字
HINT_NO_FIRST = 5  # 提示优先非首字
HINT_LAST = 6  # 提示优先尾字


def get_answer_num(e):
    answers_pos = []
    for index, val in enumerate(e):
        l = val.split(",")
        start_x = int(l[0])
        start_y = int(l[1])
        answers = l[4:]
        for index, c_val in enumerate(l[3]):
            if l[2] == "H":
                key = str(start_x + index) + '_' + str(start_y)
                if str(index) in answers:
                    answers_pos.append(key)
            else:
                key = str(start_x) + '_' + str(start_y + index)
                if str(index) in answers:
                    answers_pos.append(key)
    return len(list(set(answers_pos)))

# 获取全部坐标(不去重)
def get_all_pos(e):
    """
    获取全部坐标
    """
    all_pos = []
    for index, val in enumerate(e):
        l = val.split(",")
        start_x = int(l[0])
        start_y = int(l[1])
        for index, c_val in enumerate(l[3]):
            if l[2] == "H":
                key = str(start_x + index) + '_' + str(start_y)
            else:
                key = str(start_x) + '_' + str(start_y + index)
            all_pos.append(key)
    return all_pos

# 获取全部成语坐标
def get_all_idioms_pos(e):
    """
    获取全部坐标
    """
    all_idiom_pos = []

    for index, val in enumerate(e):
        l = val.split(",")
        start_x = int(l[0])
        start_y = int(l[1])
        pos_info = []
        for index, c_val in enumerate(l[3]):
            if l[2] == "H":
                key = str(start_x + index) + '_' + str(start_y)
            else:
                key = str(start_x) + '_' + str(start_y + index)
            pos_info.append(key)
        all_idiom_pos.append(pos_info)
    return all_idiom_pos

# 获取首字坐标
def get_first_pos(e):
    first_word_pos = []
    for index, val in enumerate(e):
        l = val.split(",")
        start_x = l[0]
        start_y = l[1]
        key = start_x + '_' + start_y
        first_word_pos.append(key)
    first_word_pos = list(set(first_word_pos))
    #print("get_first_pos ->", first_word_pos)
    return first_word_pos

# 获取尾字坐标
def get_last_pos(e):
    last_word_pos = []
    for index, val in enumerate(e):
        l = val.split(",")
        start_x = int(l[0])
        start_y = int(l[1])
        if l[2] == "H":
            key = str(start_x + len(l[3]) - 1) + '_' + str(start_y)
        else:
            key = str(start_x) + '_' + str(start_y + + len(l[3]) - 1)
        last_word_pos.append(key)
    last_word_pos = list(set(last_word_pos))
    #print("get_last_pos ->", last_word_pos)
    return last_word_pos


# 获取交叉点坐标
def get_cross_pos(e):
    """
    获取交叉点坐标
    """
    all_pos = get_all_pos(e)
    counter = Counter(all_pos)
    cross_pos = []
    for index, val in enumerate(e):
        l = val.split(",")
        start_x = int(l[0])
        start_y = int(l[1])
        for index, c_val in enumerate(l[3]):
            if l[2] == "H":
                key = str(start_x + index) + '_' + str(start_y)
            else:
                key = str(start_x) + '_' + str(start_y + index)
            if counter[key] > 1:
                cross_pos.append(key)
    cross_pos = list(set(cross_pos))
    #print("get_cross_pos ->", cross_pos)
    return cross_pos


# 检查是否出现提示整个成语
def is_hint_all(hint_list, cul_hint, e):
    """
    检查是否有全部显示的成语
    """
    all_hint_list = hint_list + [cul_hint]
    for index, val in enumerate(e):
        l = val.split(",")
        start_x = int(l[0])
        start_y = int(l[1])
        hint_num = 0
        for index, c_val in enumerate(l[3]):
            if l[2] == "H":
                key = str(start_x + index) + '_' + str(start_y)
            else:
                key = str(start_x) + '_' + str(start_y + index)
            if key in all_hint_list:
                hint_num += 1
        if hint_num >= len(l[3]):
            return True
    return False

# 根据提示字列表生成最终答案
def get_answer_by_hint(e, hint_pos_list):
    """
    根据提示字列表生成答案
    """
    new_e = []
    for index, val in enumerate(e):
        l = val.split(",")
        start_x = int(l[0])
        start_y = int(l[1])
        new_one_e = l[0] + ',' + l[1] + ',' + l[2] + ',' + l[3]
        for index, c_val in enumerate(l[3]):
            if l[2] == "H":
                key = str(start_x + index) + '_' + str(start_y)
                if key not in hint_pos_list:
                    new_one_e = new_one_e + ',' + str(index)
            else:
                key = str(start_x) + '_' + str(start_y + index)
                if key not in hint_pos_list:
                    new_one_e = new_one_e + ',' + str(index)
        new_e.append(new_one_e)
        #print(new_one_e)
    return new_e

# 提示字优先选择排序
def get_priority_hint(e, can_hint_list, hint_type_list):
    """
    提示字排序
    @param e:
    @param can_hint_list:
    @param hint_type_list:
    @return:
    """
    #print("get_priority_hint in ", can_hint_list)
    first_pos = get_first_pos(e)
    last_pos = get_last_pos(e)
    cross_pos = get_cross_pos(e)

    new_hint_type_list = []
    for can_hint_pos in can_hint_list:
        weight = 0
        for inex, hint_type in enumerate(hint_type_list):
            if hint_type == HINT_CROSS:
                if can_hint_pos in cross_pos:
                    weight += (len(hint_type_list)-inex)
            if hint_type == HINT_No_CROSS:
                if can_hint_pos not in cross_pos:
                    weight += (len(hint_type_list)-inex)
            if hint_type == HINT_FIRST:
                if can_hint_pos in first_pos:
                    weight += (len(hint_type_list)-inex)
            if hint_type == HINT_NO_FIRST:
                if can_hint_pos not in first_pos:
                    weight += (len(hint_type_list)-inex)
            if hint_type == HINT_LAST:
                if can_hint_pos in last_pos:
                    weight += (len(hint_type_list)-inex)
        new_hint_type_list.append((can_hint_pos, weight))
    new_hint_type_list = sorted(new_hint_type_list, key= lambda val: val[1], reverse=True)
    new_list = [val[0] for val in new_hint_type_list]
    #print("get_priority_hint out ", new_list)
    return new_list

# 生成答案
def get_answer(e, hint_average, hint_type_list):
    """
    重新设置答案
    提示字个数：hint_average(提示字均值)
    提示字选择类型: hint_type（0: 随机 1.优先提示交叉  2.优先提示非交叉）
    """
    print("get_answer ->",hint_average, hint_type_list)
    idiom_num = len(e)
    hint_num = int(round(hint_average*idiom_num*(float(3*idiom_num+1)/(4*idiom_num))))
    hint_average = int(hint_average)
    all_idiom_pos = get_all_idioms_pos(e)
    hint_pos_list = []
    last_can_hint = []  # 最终查缺补漏的待选序列
    # 空格数不超过32个
    if len(get_all_pos(e)) - hint_num > 32:
        hint_num = len(get_all_pos(e)) - 32
    # 平均值筛选
    #print("all_idiom_pos =>", all_idiom_pos)
    for index, idiom_pos in enumerate(all_idiom_pos):
        one_hint_list = []  # 单个成语提示字
        can_hint = []  # 备选
        # 一轮筛选出，筛选出必须提示的字和可以提示的字
        for word_pos in idiom_pos:
            if word_pos in hint_pos_list:
                # 必须提示
                one_hint_list.append(word_pos)
            else:
                is_some_idiom_all_hint = is_hint_all(hint_pos_list, word_pos, e)
                if not is_some_idiom_all_hint:
                    # 可以待选
                    can_hint.append(word_pos)
        #print("can_hint =>", can_hint)
        # 有待选,并且未达到提示的平均值
        if len(one_hint_list) < hint_average and len(can_hint) > 0:
            # 二轮筛选(优先选择)
            can_hint = get_priority_hint(e, can_hint, hint_type_list)
            diff = hint_average - len(one_hint_list)
            one_hint_list = can_hint[0:diff]
            last_can_hint.append(can_hint[diff:])
        else:
            last_can_hint.append(can_hint)
        # 加入总的提示字列表
        hint_pos_list += [val for val in one_hint_list]
    # 查缺补漏筛选
    hint_pos_list = list(set(hint_pos_list))
    loop = 0
    # print("hint_pos_list ->", hint_pos_list)
    # print("last_can_hint =>", last_can_hint)
    while (len(hint_pos_list) < hint_num):
        random.shuffle(last_can_hint)
        last_can_hint = sorted(last_can_hint, key=lambda val: len(val), reverse=True)  # 保持平均
        last_can_hint = [val for val in last_can_hint if len(val) > 0]
        if len(last_can_hint) <= 0:
            break
        for index, val in enumerate(last_can_hint):
            if len(hint_pos_list) >= hint_num:
                break
            del_some_idiom_all_hint = []
            for val_1 in val:
                is_some_idiom_all_hint = is_hint_all(hint_pos_list, val_1, e)
                if is_some_idiom_all_hint:
                    del_some_idiom_all_hint.append(val_1)
                else:
                    # 可以待选
                    hint_pos_list.append(val_1)
                    break
            for del_val in del_some_idiom_all_hint:
                last_can_hint[index].remove(del_val)
        loop += 1
        if loop > 50:
           break
    hint_pos_list = list(set(hint_pos_list))
    new_e = get_answer_by_hint(e, hint_pos_list)
    #print(new_e)
    return new_e


# e= [
#         u"3,2,H,唯唯诺诺,0,1,2",
#         u"3,0,V,任人唯亲,0,1,2",
#         u"5,1,V,一诺千金,0,1,2",
#         u"1,0,H,选贤任能,0,1,2",
#         u"0,3,H,举目无亲,0,1,2",
#         u"4,4,H,拾金不昧,0,2,3",
#         u"0,3,V,举手之劳,0,1,2",
#         u"2,3,V,无所顾忌,0,1,2",
#         u"4,4,V,拾人牙慧,0,1,2",
#         u"6,4,V,不足为虑,0,1,2"
#         ]
# get_answer(e, 0.5, [6,3])