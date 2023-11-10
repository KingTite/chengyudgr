# -*- coding=utf-8  -*-

import json
import codecs

"""
主要功能：
1. 简体转换成繁体 
2. 检查繁体错误
3. 删除不能转化成繁体的题目
"""
# 简体对应的繁体字典
ft_idioms_file = '../data/jt_ft_idiom.json'


# 简体转换成繁体
def jt_to_ft(e):
    """
    简体转化成繁体
    """
    new_e = []
    with open(ft_idioms_file, 'r') as f:
        ft_idioms = json.loads(f.read())

    for e_index, e_val in enumerate(e):
        s_to_l = e_val.split(',')
        if s_to_l[3] not in ft_idioms:
            print("err", s_to_l[3])
            return None
        else:
            s_to_l[3] = ft_idioms[s_to_l[3]]
            l_to_s = ','.join(s_to_l)
            new_e.append(l_to_s)
    return new_e


# 检查繁体错误（判断同一个位置汉字是否相同）
def is_pos_word_equal(e):
    """
    同一个位置汉字是否相同
    @return:
    """
    all_pos_val = {}
    # 全部坐标
    for index, val in enumerate(e):
        l = val.split(",")
        start_x = int(l[0])
        start_y = int(l[1])
        for index, c_val in enumerate(l[3]):
            if l[2] == "H":
                key = str(start_x + index) + '_' + str(start_y)
                if key not in all_pos_val:
                    all_pos_val[key] = c_val
                else:
                    if c_val != all_pos_val[key]:
                        print(c_val)
                        print(all_pos_val[key])
                        return False
            else:
                key = str(start_x) + '_' + str(start_y + index)
                if key not in all_pos_val:
                    all_pos_val[key] = c_val
                else:
                    if c_val != all_pos_val[key]:
                        print(c_val)
                        print(all_pos_val[key])
                        return False
    return True


# 删除不能转化成繁体的题目
def del_not_to_ft(question_list):
    print("del_not_to_ft in ", len(question_list))
    new_list = []
    for index, val in enumerate(question_list):
        new_e = jt_to_ft(val['e'])
        if not new_e:
            continue
        is_equal = is_pos_word_equal(new_e)
        if not is_equal:
            print(" del_not_to_ft err", val['id'])
            continue
        val['id'] = len(new_list) + 1
        new_list.append(val)
    print("del_not_to_ft out ", len(new_list))
    return new_list

