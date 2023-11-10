# -*- coding=utf-8  -*-

import json
import codecs
import random
import format_tiku
import time

"""
生成题库入口
4*4 -> 3
5*5 -> 4
6*6 -> 5/6
7*7 -> 7/8
8*8 -> 9/10/11
9*9 -> 12/13/14/15
"""

# 最大行列限制
MAX_X = 7
MAX_Y = 7

# 最少成语个数限制
MIN_IDIOMS = 7

XIAOJI_PRO = 3  # 消极概率
PIANPI_PRO = 20  # 偏僻题概率
CHANGJIAN_PRO = 77  # 常见概率

QUTION_COUNT = 3000  # 题目数量

START = True  # 是否执行

INIT_IDIOMS = True  # 是否初始化成语题库


# 常见成语库文件名
changjian_file_name = "../data/changjian"
# 偏僻成语库文件名
pianpi_file_name = "../data/pianpi"
# 消极成语库文件名
xiaoji_file_name = "../data/xiaoji"

# 生成的题库,待处理
tiku_dir = "../pending/"


# 初始化所有成语库状态
def init_idioms():
    """
    初始化3个题库
    """
    with open(changjian_file_name + '.json', 'r') as f:
        changjian = json.loads(f.read())
    with open(pianpi_file_name + '.json', 'r') as f:
        pianpi = json.loads(f.read())
    with open(xiaoji_file_name + '.json', 'r') as f:
        xiaoji = json.loads(f.read())

    init_changjian = {val: 0 for val in changjian}
    init_pianpi = {val: 0 for val in pianpi}
    init_xiaoji = {val: 0 for val in xiaoji}

    with codecs.open(changjian_file_name + '_ing.json', 'w', 'utf-8') as f:
        json.dump(init_changjian, f, indent=4, sort_keys=True, ensure_ascii=False)

    with codecs.open(pianpi_file_name + '_ing.json', 'w', 'utf-8') as f:
        json.dump(init_pianpi, f, indent=4, sort_keys=True, ensure_ascii=False)

    with codecs.open(xiaoji_file_name + '_ing.json', 'w', 'utf-8') as f:
        json.dump(init_xiaoji, f, indent=4, sort_keys=True, ensure_ascii=False)


# 成语出现个数相加
def add_count(idiom):

    with open(changjian_file_name + '_ing.json', 'r') as f:
        changjian = json.loads(f.read())
    with open(pianpi_file_name + '_ing.json', 'r') as f:
        pianpi = json.loads(f.read())
    with open(xiaoji_file_name + '_ing.json', 'r') as f:
        xiaoji = json.loads(f.read())

    # 常见成语使用次数+1
    if idiom in changjian:
        changjian[idiom] += 1
        with codecs.open(changjian_file_name + '_ing.json', 'w', 'utf-8') as f:
            json.dump(changjian, f, indent=4, sort_keys=True, ensure_ascii=False)
    # 偏僻成语数量+1
    if idiom in pianpi:
        pianpi[idiom] += 1
        with codecs.open(pianpi_file_name + '_ing.json', 'w', 'utf-8') as f:
            json.dump(pianpi, f, indent=4, sort_keys=True, ensure_ascii=False)
    # 消极成语使用数量+1
    if idiom in xiaoji:
        xiaoji[idiom] += 1
        with codecs.open(xiaoji_file_name + '_ing.json', 'w', 'utf-8') as f:
            json.dump(xiaoji, f, indent=4, sort_keys=True, ensure_ascii=False)


# 按概率选择成语库
def probability_choose_idioms():
    """
    根据题库的概率，选出对应题库
    """
    with open(changjian_file_name + '_ing.json', 'r') as f:
        d_changjian = json.loads(f.read())
    with open(pianpi_file_name + '_ing.json', 'r') as f:
        d_pianpi = json.loads(f.read())
    with open(xiaoji_file_name + '_ing.json', 'r') as f:
        d_xiaoji = json.loads(f.read())

    l_xiaoji_list = [(key, val) for key, val in d_xiaoji.items()]
    l_pianpi_list = [(key, val) for key, val in d_pianpi.items()]
    l_changjian_list = [(key, val) for key, val in d_changjian.items()]

    l_xiaoji_sort_list = [val1[0] for val1 in sorted(l_xiaoji_list, key=lambda val: val[1])]
    l_pianpi_sort_list = [val1[0] for val1 in sorted(l_pianpi_list, key=lambda val: val[1])]
    l_changjian_sort_list = [val1[0] for val1 in sorted(l_changjian_list, key=lambda val: val[1])]


    while 1:
        # 生成随机数
        l_rand = random.randint(0, 100)
        # 选取
        if l_rand < XIAOJI_PRO:
            cul_idioms = l_xiaoji_sort_list + l_changjian_sort_list + l_pianpi_sort_list
            return cul_idioms

        if l_rand < PIANPI_PRO:
            cul_idioms = l_pianpi_sort_list + l_changjian_sort_list + l_xiaoji_sort_list
            return cul_idioms

        if l_rand < CHANGJIAN_PRO:
            cul_idioms = l_changjian_sort_list + l_pianpi_sort_list + l_xiaoji_sort_list
            return cul_idioms


# 保存题库
def save_result(result, file_index=0):
    """
    生成题目文件
    @param result:
    @param file_index:
    @return:
    """
    result_question_list = format_tiku.get_format_word_now(result)
    path = tiku_dir + str(MAX_X) + '_' + str(MIN_IDIOMS) + '/'
    file_name = str(MAX_X) + '_' + str(MIN_IDIOMS) + '_' + str(file_index) + '.json'
    with codecs.open(path+file_name, 'w', 'utf-8') as f:
        json.dump(result_question_list, f, indent=4, sort_keys=True, ensure_ascii=False)


# 尽可能多的生成题目
def get_more_word_list(tiku_file_name, run_times=5):
    with open(tiku_file_name + '.json', 'r') as f:
        all_idiom = json.loads(f.read())
    all_idiom = all_idiom
    result = []
    file_index = 0  # 文件编号
    total_num = 0  # 生成题的总数
    # 返回值说明： 0全部循环结束， 1主动终止
    for index, idiom in enumerate(all_idiom):
        print("id ->", index, "sum -> ", len(result), file_index)
        # 填词
        one_idiom_first_list = creat_cross_map(idiom, run_times)
        if one_idiom_first_list:
            result += one_idiom_first_list
            total_num += len(one_idiom_first_list)

        # 一定数量缓存
        if len(result) >= 100:
            save_result(result, file_index)
            file_index += 1
            result = []
    return 0

# 生成指定数量题目
def get_definite_question(run_times=3):
    loop_index = 0
    loop_max = 5000  # 最大循环次数
    result = []
    file_index = 0  # 文件编号
    cul_qustion_num = 0  # 当前题目数量
    # 返回值说明： 0全部循环结束， 1主动终止， 2 到达指定数量
    while loop_index < loop_max:
        loop_index += 1
        print("loop_index -> ", loop_index)
        print("quetion_sum -> ", cul_qustion_num)
        # 确定第一个成语
        start_time = int(time.time())
        cul_idioms = probability_choose_idioms()
        first_idiom = cul_idioms[0]
        add_count(first_idiom)
        print(first_idiom)
        # 填充其他成语
        one_idiom_first_list = creat_cross_map(first_idiom, run_times)
        if one_idiom_first_list:
            result += one_idiom_first_list
            cul_qustion_num += len(one_idiom_first_list)

        # 隔一定数量保存， 防止丢失过多， 或者单个文件过大
        if len(result) >= 100:
            save_result(result, file_index)
            file_index += 1
            result = []

        # 到达指定数量
        if cul_qustion_num > QUTION_COUNT:
            save_result(result, file_index)
            return 2

        # 执行开关
        if not START:
            save_result(result, file_index)
            return 1
        print("cost_time -> ", str(int(time.time()) - start_time) + 's')
        print("------------------------------------------------")
    return 0

# 生成坐标和字符列表（判断单词是否可以正确填入）
def creat_word_x_y_c(word, _dir, start_x, start_y, full_x_y_c, cross_char_pos=None):
    x_y_c = {}
    if not is_in_range(start_x, start_y, _dir, full_x_y_c, word):
        return None, None
    if _dir == 'H':  # 横
        # 前一列 是否已经填字母
        if str(start_x - 1) + '_' + str(start_y) in full_x_y_c:
            return None, None
        # 最后-列 是否已经填字母
        if str(start_x + len(word)) + '_' + str(start_y) in full_x_y_c:
            return None, None
        for index, c in enumerate(word):
            # 相交词除外
            if (start_x + index) != None and (start_x + index) != cross_char_pos:
                # 上一行 是否已经填字母
                if str(start_x+index)+'_'+str(start_y-1) in full_x_y_c:
                     return None, None
                # 下一行 是否已经填字母
                if str(start_x+index)+'_'+str(start_y+1) in full_x_y_c:
                    return None, None
            # 当前位置是否已经填字母
            key = str(start_x + index) + '_' + str(start_y)
            if (key in full_x_y_c) and (full_x_y_c[key] != c):
                return None, None
            x_y_c.update({key: c})
    else:  # 竖
        # 上一行 是否已经填字母
        if str(start_x) + '_' + str(start_y-1) in full_x_y_c:
            return None, None
        # 结尾行 是否已经填字母
        if str(start_x) + '_' + str(start_y+len(word)) in full_x_y_c:
            return None, None
        for index, c in enumerate(word):
            # 相交词除外
            if (start_y+index) != None and (start_y+index) != cross_char_pos:
                # 上一列 是否已经填字母
                if str(start_x-1)+'_'+str(start_y+index) in full_x_y_c:
                    return None, None
                # 下一列 是否已经填字母
                if str(start_x+1)+'_'+str(start_y+index) in full_x_y_c:
                    return None, None
            # 当前位置是否已经填字母
            key = str(start_x)+'_'+str(start_y+index)
            if (key in full_x_y_c) and (full_x_y_c[key] != c):
                    return None, None
            x_y_c.update({key: c})
    # 返回答案
    answer = random.choice(x_y_c.keys())
    return x_y_c, answer


# 获取最小坐标和最大坐标
def get_start_end(full_x_y_c, _dir='H'):
    start = 99999
    end = -9999
    for key, val in full_x_y_c.items():
        x, y = key.split('_')
        if _dir == 'H':
            start = min(int(x), start)
            end = max(int(x), end)
        else:
            start = min(int(y), start)
            end = max(int(y), end)
    return start, end

# 获取结束长度
def get_end_pos(start_x, start_y, _dir, idiom):
    word_end_x = start_x
    word_end_y = start_y
    if _dir == 'H':
        word_end_x = start_x + len(idiom)-1
    else:
        word_end_y = start_y + len(idiom)-1

    return word_end_x, word_end_y

# 判断摆放是否超过最大行和列
def is_in_range(word_start_x, word_start_y, _dir, full_x_y_c, word):
    start_x = 0
    end_x = 0
    start_y = 0
    end_y = 0
    word_end_x, word_end_y = get_end_pos(word_start_x, word_start_y, _dir, word)
    for key, val in full_x_y_c.items():
        x, y = key.split('_')
        start_x = min(int(x), start_x, word_start_x, word_end_x)
        end_x = max(int(x), end_x, word_start_x, word_end_x)
        start_y = min(int(y), start_y, word_start_y, word_end_y)
        end_y = max(int(y), end_y,  word_start_y, word_end_y)

    if (end_x - start_x) >= MAX_X:
        return False
    if (end_y - start_y) >= MAX_Y:
        return False
    return True



# 获取一行的字符
def get_one_line_chars(lin_index, full_x_y_c, _dir):
    line_chars = []
    for key, val in full_x_y_c.items():
        pos = key.split('_')
        if _dir == 'H':  # 横行
            if lin_index == int(pos[1]):
                line_chars.append((int(pos[0]),val))
        if _dir == 'V':
            if lin_index == int(pos[0]):
                line_chars.append((int(pos[1]), val))
    return line_chars


# 获取单词的起始坐标
def get_start_pos(word, cross_c, c_x, c_y, _dir):
    point = None
    for index, c in enumerate(word):
        if c == cross_c:
            point = index
            break
    if point != None:
        if _dir == 'H':
            start_x = int(c_x) - point
            start_y = int(c_y)
        else:
            start_x = int(c_x)
            start_y = int(c_y) - point
    else:
        return None, None
    return start_x, start_y


# 获取当前直线可匹配字的符串
def get_one_line_cross_chars(line_index):
    sort_line_index = sorted(line_index)  # 按坐标排序
    result_list = []
    if len(sort_line_index) == 1:
        result_list.append(sort_line_index[0])
    else:
        for i in range(0, len(sort_line_index)-1):
            if (sort_line_index[i+1][0] - sort_line_index[i][0]) > 1:
                # 最后一个
                if i + 1 == len(sort_line_index) - 1:
                    result_list.append(sort_line_index[i+1])
                # 第一个
                if i == 0:
                    result_list.append(sort_line_index[i])
                else:
                    if (sort_line_index[i][0] - sort_line_index[i-1][0]) > 1:
                        result_list.append(sort_line_index[i])
    return result_list

# 遍历所有行或者所有列填词
def all_lins_in_word(start_line, end_line, full_x_y_c, in_map_word, answers, curr_dir):
    l_x_y_c = full_x_y_c
    l_map_word = in_map_word
    l_answers = answers
    for i in range(start_line, end_line + 1):
        # 获取当前直线上字母
        one_line_chars = get_one_line_chars(i, l_x_y_c, curr_dir)
        # 获取可以相交的字母列表
        cross_chars = get_one_line_cross_chars(one_line_chars)
        for one_cross_chars in cross_chars:
            # 按概率筛选成语题库(优先概率成语)
            now_idioms = probability_choose_idioms()
            for idiom in now_idioms:
                if idiom in in_map_word:
                    continue
                if curr_dir == 'H':
                    start_x, start_y = get_start_pos(idiom, one_cross_chars[1], int(one_cross_chars[0]), i, curr_dir)
                else:
                    start_x, start_y = get_start_pos(idiom, one_cross_chars[1], i, int(one_cross_chars[0]), curr_dir)
                if start_x == None:
                    continue
                x_y_c, answer = creat_word_x_y_c(idiom, curr_dir, start_x, start_y, l_x_y_c, int(one_cross_chars[0]))
                if not x_y_c:
                    continue
                l_x_y_c.update(x_y_c)
                l_map_word.append(idiom)
                l_answers.append(answer)
                add_count(idiom)
                break
    return l_x_y_c, l_map_word, l_answers

# 获取最大行和最大列
def get_max_x_y(full_x_y_c):
    start_x = 0
    end_x = 0
    start_y = 0
    end_y = 0
    for key, val in full_x_y_c.items():
        x, y = key.split('_')
        start_x = min(int(x), start_x)
        end_x = max(int(x), end_x)
        start_y = min(int(y), start_y)
        end_y = max(int(y), end_y)

    max_x = end_x - start_x + 1
    max_y = end_y - start_y + 1
    return max_x, max_y

# 选出最优解
def get_better(some_kinds):
    # 按剩余没填最少排序
    some_kinds = sorted(some_kinds, key=lambda val: len(val['no_in_map']))
    # 筛选出剩余并列最少的全部
    better_list = list(filter(lambda val: len(val['no_in_map']) == len(some_kinds[0]['no_in_map']), some_kinds))
    # 筛选出一个表格最少的
    better_list = sorted(better_list, key=lambda val: val['max_size'])
    return better_list[0]
# 格式化
def get_format(_d):
    new_d = {
        "idiom": _d['in_map_word'],
        "posx": [],
        "posy": [],
        "word": [],
        "answer": [],
        "lines": _d['lines']
    }
    index = 0
    for key, val in _d['full_x_y_c'].items():
        s_to_l = key.split('_')
        new_d['posx'].append(int(s_to_l[0]))
        new_d['posy'].append(int(s_to_l[1]))
        new_d['word'].append(val)
        if key in _d['answers']:
            new_d['answer'].append(index)
        index += 1
    return new_d

# 填词主要函数
def creat_cross_map(first_idiom, run_times):
    result = []
    for i in range(0, run_times):
        full_x_y_c = {}  # 填好的{坐标:字母}列表
        in_map_word = []  # 填好的单词列表
        answers = []
        # 初始摆放方向
        curr_x_y_word, answer = creat_word_x_y_c(first_idiom, 'H', 0, 0, full_x_y_c)
        full_x_y_c.update(curr_x_y_word)
        in_map_word.append(first_idiom)  # 填好的单词列表
        answers.append(answer)
        curr_dir = 'H'  # 初始摆放方向
        # 填词
        run = 0
        while run <= 3:
            if curr_dir == 'H':
                # 竖着排，遍历横坐标
                curr_dir = 'V'
                start_line, end_line = get_start_end(full_x_y_c, 'H')
                full_x_y_c, in_map_word, answers = all_lins_in_word(start_line, end_line, full_x_y_c, in_map_word, answers, curr_dir)
            if curr_dir == 'V':
                # 竖着排，遍历横坐标
                curr_dir = 'H'
                start_line, end_line = get_start_end(full_x_y_c, 'V')
                full_x_y_c, in_map_word, answers = all_lins_in_word(start_line, end_line, full_x_y_c, in_map_word, answers, curr_dir)
            run += 1
        # 每组单词数量控制
        if len(in_map_word) != MIN_IDIOMS:
            continue
        _d = {
            'full_x_y_c': full_x_y_c,
            'in_map_word': in_map_word,
            'answers': list(set(answers)),
            'lines': format_print(full_x_y_c)
        }
        # 格式化输出
        result.append(get_format(_d))
    return result


# 格式化输出
def format_print(d_x_y_c):
    lines = []
    min_x = 0
    min_y = 0
    max_x = 0
    max_y = 0
    for key, val in d_x_y_c.items():
        s_to_l = key.split('_')
        min_x = min(int(s_to_l[0]), min_x)
        max_x = max(int(s_to_l[0]), max_x)
        min_y = min(int(s_to_l[1]), min_y)
        max_y = max(int(s_to_l[1]), max_y)
    for y in range(min_y, max_y+1):
        line = ''
        for x in range(min_x, max_x+1):
            key = str(x) + '_' + str(y)
            if key in d_x_y_c:
                line += d_x_y_c[key] + '|'
            else:
                line += u'口|'
        #print(line)
        lines.append(line)
    #print("-----------------------------------------------------")
    return lines

# 开始生成入口
def run():
    """
    生成题库入口
    """
    # 初始成语库
    if INIT_IDIOMS:
        init_idioms()

    # 生成题库
    start_time = int(time.time())
    get_definite_question(3)
    print("get_definite_question cost_time -> ", str(int(time.time()) - start_time) + 's')


run()