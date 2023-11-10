# -*- coding=utf-8  -*-

"""
生成题库文件转化成程序需要的数据格式
"""

from operator import itemgetter
from itertools import groupby

MIN_IDIOM_LEN = 4


# y坐标转化
def posy_to_format(posy_list):
    min_x = min(posy_list)
    return [val - min_x for val in posy_list]

# x坐标转化
def posx_to_format(posx_list):
    min_x = min(posx_list)
    return [val-min_x for val in posx_list]

# 获取的汉字列表 是否完全等于成语
def is_eque_idiom(l_idiom, idiom):
    for index, val in enumerate(l_idiom):
        if val != idiom[index]:
            return False
    return True

def get_word_index(words, posx_list, posy_list, idiom):
    file_words_index = [index for index, word in enumerate(words) if word in idiom]
    if len(file_words_index) >= MIN_IDIOM_LEN:
        # 按横坐标相等分组
        sort_file_words_index = sorted(file_words_index, key=lambda val: posx_list[val])
        for k_x, g_x in groupby(sort_file_words_index, lambda x: posx_list[x]):
            x_eql_l = list(g_x)
            result = sorted(x_eql_l, key=lambda val: posy_list[val])
            if len(result) >= MIN_IDIOM_LEN:
                # 按纵坐标连续分组
                for k, g in groupby(enumerate(result), lambda (i, x): i - posy_list[x]):
                    m = map(itemgetter(1), g)
                    if len(m) >= MIN_IDIOM_LEN and is_eque_idiom([words[val] for val in m], idiom):
                        return m

        # 按纵坐标相等分组
        sort_file_words_index = sorted(file_words_index, key=lambda val: posy_list[val])
        for k_y, g_y in groupby(sort_file_words_index, lambda x: posy_list[x]):
            y_eql_l = list(g_y)
            result = sorted(y_eql_l, key=lambda val: posx_list[val])
            if len(result) >= MIN_IDIOM_LEN:
                # 按横坐标连续分组
                for k, g in groupby(enumerate(result), lambda (i, x): i - posx_list[x]):  # 按横坐标连续分组
                    m = map(itemgetter(1), g)
                    if len(m) >= MIN_IDIOM_LEN and is_eque_idiom([words[val] for val in m], idiom):
                        return m
    print(" get_word_index err ")
    return None

def get_idiom_fomat(d_idiom):
    e_list = []
    idiom_list = d_idiom['idiom']
    words = d_idiom['word']
    answers = d_idiom['answer']
    posx_list = posx_to_format(d_idiom['posx'])
    posy_list = posy_to_format(d_idiom['posy'])
    for idiom in idiom_list:
        # 成与每个字的索引(完全按顺序)
        idiom_index = get_word_index(words, posx_list, posy_list, idiom)   # 成与每个字的索引
        word_start_x = posx_list[idiom_index[0]]
        word_start_y = posy_list[idiom_index[0]]
        # 方向判断
        dir = 'R'  # 横
        if len(set([posx_list[val] for val in idiom_index])) == 1:  # 竖
            dir = 'V'
        elif len(set([posy_list[val] for val in idiom_index])) == 1:  # 横
            dir = 'H'
        else:
            print("dir err")
        # 答案判断
        idiom_anser_index = []
        for i_i, i_v in enumerate(idiom_index):
            if i_v in answers:
                idiom_anser_index.append(str(i_i))
        anser_str = ','.join(sorted(list(set(idiom_anser_index))))
        # 合成最终字符串
        if anser_str:
            str_e = str(word_start_x) + ',' + str(word_start_y) + ',' + dir + ',' + idiom + ',' + anser_str
        else:
            str_e = str(word_start_x) + ',' + str(word_start_y) + ',' + dir + ',' + idiom
        e_list.append(str_e)
    return e_list


def get_format_word_now(question_list):
    """
    手动生成的题库和小秀才题库，都需要该方法转换成我们必要的格式
    """
    # 生成题库(数据转化)
    print("get_format_word_now in ->", len(question_list))
    new_list = []
    for index, d_idiom in enumerate(question_list):
        new_d = {}
        new_d['e'] = get_idiom_fomat(d_idiom)
        new_d['id'] = index + 1
        new_d['lines'] = d_idiom['lines']
        new_list.append(new_d)
    print("get_format_word_now out ->", len(new_list))
    return new_list



