# -*- coding=utf-8  -*-

import json
import os

# 获取全部坐标
def get_all_pos(e):
    """
    获取全部坐标
    """
    all_pos = []
    all_idiom_pos = []
    for index, val in enumerate(e):
        l = val.split(",")
        start_x = int(l[0])
        start_y = int(l[1])
        idiom_pos = []
        for index, c_val in enumerate(l[3]):
            if l[2] == "H":
                key = str(start_x + index) + '_' + str(start_y)
            else:
                key = str(start_x) + '_' + str(start_y + index)
            all_pos.append(key)
            idiom_pos.append(key)
        all_idiom_pos.append(idiom_pos)
    return all_pos, all_idiom_pos


def is_inline(e):
    """
    校验题目是否全部相连
    """
    all_pos, all_idiom_pos = get_all_pos(e)
    one_line = all_idiom_pos.pop(0)
    loop = True
    while loop:
        add = False
        for index, val in enumerate(all_idiom_pos):
            if len(list(set(val + one_line))) < len(val + one_line):
                one_line = list(set(one_line + all_idiom_pos.pop(index)))
                add = True
                break
        if not add:
            break
    if len(list(set(all_pos))) == len(list(set(one_line))):
        return True
    else:
        return False

def get_answer_num(e):
    """
    获取答案数量
    """
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

# 统计答案超过32的题目
def get_answer_num_more_32():
    """
    校验答案数量是否超过32
    @return:
    """
    tiku_dir = os.listdir("new_tiku_100_ft/")
    for filename in tiku_dir:
        with open("new_tiku_100_ft/" + filename, 'r') as f:
            l = json.loads(f.read())
        for index, val in enumerate(l):
            if get_answer_num(val['e']) > 32:
                print("err " + "new_tiku_100_ft/" + filename + ' ' +  str(val['id']))

def check_jx_all():
    for index in range(1, 51):
        with open("jx_tiku_2000/ft/jxtiku_f" + str(index) + ".json", 'r') as f:
            _d = json.loads(f.read())
        for key, val in _d.items():
            if not is_inline(val['e']):
                print("err ->", index, key)


def check_main_all():
    for index in range(1, 88):
        with open("new_tiku_100_ft/tiku_f" + str(index) + ".json", 'r') as f:
            l = json.loads(f.read())
        for index, val in enumerate(l):
            if not is_inline(val['e']):
                print("err ->", index, index)


get_answer_num_more_32()
