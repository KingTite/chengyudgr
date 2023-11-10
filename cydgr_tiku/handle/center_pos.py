# -*- coding=utf-8  -*-

import json
import codecs
from collections import Counter

"""
小于 9*9坐标居中处理
"""

LIMIT_X_Y = 9

def init_pos(e):
    """
    坐标初始化以0，0为原点
    """
    min_x = 100
    min_y = 100
    for val in e:
        l = val.split(",")
        min_x = min(min_x, int(l[0]))
        min_y = min(min_y, int(l[1]))
    for index, val in enumerate(e):
        l = val.split(",")
        l[0] = str(int(l[0]) - min_x)
        l[1] = str(int(l[1]) - min_y)
        e[index] = ','.join(l)
    #print(e)
    return e


def get_center_pos(e):
    """
    获取去最大x, y 和 x, y 平均值 (董阳阳算法)
    @return:
    """
    max_x = -100
    max_y = -100
    total_x = 0
    total_y = 0
    pos = []
    e = init_pos(e)
    for val in e:
        l = val.split(",")
        for e_i, e_v in enumerate(l[3]):
            if l[2] == 'H':
                pos_key = str(int(l[0]) + e_i) + ',' + l[1]
                pos.append(pos_key)
                max_x = max(max_x, int(l[0]) + e_i)
                max_y = max(max_y, int(l[1]))
            else:
                pos_key = l[0] + ',' + str(int(l[1]) + e_i)
                pos.append(pos_key)
                max_x = max(max_x, int(l[0]))
                max_y = max(max_y, int(l[1]) + e_i)


    max_x += 1
    max_y += 1

    pos = list(set(pos))
    for pos_val in pos:
        x_y = pos_val.split(",")
        total_x += int(x_y[0])
        total_y += int(x_y[1])
    p_x = total_x/float(len(pos))
    p_y = total_y/float(len(pos))

    x_0 = (max_x - (max_x % 2)) / 2
    y_0 = (max_y - (max_y % 2)) / 2

    add_x = 0
    if max_x < LIMIT_X_Y and (p_x - x_0 <= -0.75):
        add_x = 1

    add_y = 0
    if max_y < LIMIT_X_Y and (p_y - y_0 <= -0.75):
        add_y = 1

    # print(len(pos), max_x, max_y, total_x, total_y, p_x, p_y, x_0, y_0, add_x, add_y)

    for e_index, e_val in enumerate(e):
        l = e_val.split(",")
        l[0] = str(int(l[0]) + add_x)
        l[1] = str(int(l[1]) + add_y)
        e[e_index] = ','.join(l)
    # print(e)
    return e


def one_question_pos(question):
    """
    单个题目获取新的坐标
    """
    new_e = get_center_pos(question['e'])
    question['e'] = new_e
    return question

