# -*- coding=utf-8  -*-
"""
极限挑战题库生成
汉字数量不超过34个，每题两个不空的字
"""

import json
import codecs
import random

# hard题库处理前目录
init_hard_dir = "../pending/hard/init_hard_tiku.json"
hard_tiku_dir = "../pending/hard/hard_tiku/"

def file_hard_tiku():
    with open(init_hard_dir, 'r') as f:
        all_idiom = json.loads(f.read())
    result = []
    new_id = 0
    for index, val in enumerate(all_idiom):
        print("index: ", index + 1)
        pos = []
        new_e = []
        for e_v in val['e']:
            e_v_l = e_v.split(',')
            new_e.append(','.join(e_v_l[:4]))
            if e_v_l[2] == 'H':
                pos.append(e_v_l[0] + ',' + e_v_l[1])
                pos.append(str(int(e_v_l[0])+1) + ',' + e_v_l[1])
                pos.append(str(int(e_v_l[0]) + 2) + ',' + e_v_l[1])
                pos.append(str(int(e_v_l[0]) + 3) + ',' + e_v_l[1])
            else:
                pos.append(e_v_l[0] + ',' + e_v_l[1])
                pos.append(e_v_l[0] + ',' + str(int(e_v_l[1])+1))
                pos.append(e_v_l[0] + ',' + str(int(e_v_l[1])+2))
                pos.append(e_v_l[0] + ',' + str(int(e_v_l[1])+3))
        if len(list(set(pos))) <= 34:
            new_id += 1
            if len(new_e)-1 > 2:
                show_list = random.sample(range(0, len(new_e)-1), 2)
            else:
                show_list = [0,1]
            rand_words = []
            for show_index in show_list:
                new_e_l = new_e[show_index].split(',')
                randint = random.randint(0, 3)
                if new_e_l[3][randint] not in rand_words:
                    new_e[show_index] = new_e[show_index] + ',' + str(randint)
            _d = {
                "id": new_id,
                'e': new_e
            }
            result.append(_d)
    return result


# 拆分题库
def split_file(question_list):

    file_index = 1
    question_num = 1
    _d = {}
    for index, val in enumerate(question_list):
        key = "level_" + str(question_num)
        _d[key] = val
        question_num += 1
        if question_num > 40:
            with codecs.open(hard_tiku_dir + 'jxtiku_f'+str(file_index)+'.json', 'w', 'utf-8') as f:
                json.dump(_d, f, indent=4, sort_keys=True, ensure_ascii=False)
            question_num = 1
            _d = {}
            file_index += 1


step = file_hard_tiku()
split_file(step)
