# -*- coding=utf-8  -*-

import json
import codecs
from collections import Counter
import random
import os
from center_pos import one_question_pos

"""
    题库的一些处理方法
    # 合并目录下文件 merge_file_dir()
    # 题库去重（可以选择是否先去除高频词）:check_repeat()
    # 获取全部坐标：get_all_pos()
    # 获取题库列表差集: get_difference_list()
    # 统计成语使用次数: idioms_use_times()
    # 去除含有某些词的题: del_include_some_idioms()
    # 获取偏僻题数量: get_pianpi_num()
    # 筛选出成语数量和偏僻词数量相等的题目:get_limit_idioms_num()
    # 获取题目行列和: get_question_max_x_y()
    # 按行列和筛选: filter_max_x_y()
    # 按行列相加排序: sort_min_x_y()
    # 按偏僻词数量排序: sort_pianpi_num()
    # 调整重心: question_center_pos()
    # 疏散相同成语分布: evacuate_same_idiom()
    # 过滤给定id的题库:del_some_id()
    # 统计不同成语个数的题量：idiom_num_dict()
    # 统计全部成语：get_all_idioms（）, get_all_idioms_no_set()
    # 成语库分类: different_idioms()
    # 题库排序Id: sort_id()
    # 获取固定偏僻词数量的题: get_pianpi_pro()
    # 按成语个数分类： different_by_idioms_num()
    # 部分题目插入题库: add_question()
    # 拆分文件100题1个文件: split_file()
    # 统计id之前的成语数量:sort_id_idiom_num()
    # 合并有序文件: merge_sort_file()
    # 去除空格和换行:json_replace()
    # 扩充简繁映射:add_jt_to_ft_map()
    # 删除使用相同成语过多的题目:del_too_many_use()
    # 获取题目在成语列表出现的成语数量：include_idioms_num()
    # 获取整个题目成语出现频率总和：question_all_idim_use_times(）
    # 检查题目是否在列表中存在: one_check_repeat()
    # 判断 左上角空3*3、右上角3*3、左下角3*3、右下角3*3，对角线2*4 ：is_space_reach(question)
    # 过滤掉空格过多的题目 
    # 一个题目加入到储备题库： question_add_store_tiku(question)
    # 近义词和乌龙词不能出现在同一个成语中  is_like_idoms()
"""

# 常见成语库文件名
changjian_file_name = "../data/changjian"
# 偏僻成语库文件名
pianpi_file_name = "../data/pianpi"
# 消极成语库文件名
xiaoji_file_name = "../data/xiaoji"
# 近义词
jinyi_file_name = "../data/jinyi_idiom.json"
# 乌龙词
wulong_file_name = "../data/wulong_idiom.json"
# 准备好的题库目录
ready_split_dir = "../ready/split/"
# 储备题库目录
store_dir = "../store/diff_pianpi/"


# 合并目录下文件
def merge_file_dir(s_dir_path, d_dir_path=None, split=-1):
    """
    合并固定目录下的文件，可以选择再切分
    """
    all_list = []
    files = os.listdir(s_dir_path)
    for filename in files:
        print(s_dir_path + filename)
        with open(s_dir_path + filename, 'r') as f:
            all_list += json.loads(f.read())

    if split > 0 and len(all_list) > split:
        split_list = [all_list[i:i + split] for i in range(0, len(all_list), split)]
        for index, val in enumerate(split_list):
            print(index, len(val))
            with codecs.open(d_dir_path + '_' + str(index) + '.json', 'w', 'utf-8') as f:
                json.dump(val, f, indent=4, sort_keys=True, ensure_ascii=False)
    else:
        if d_dir_path:
            with codecs.open(d_dir_path + '_' + 'all.json', 'w', 'utf-8') as f:
                json.dump(all_list, f, indent=4, sort_keys=True, ensure_ascii=False)

    print("merge_file_dir -> ", len(all_list))
    return all_list

# 合并有序文件
def merge_sort_file(s_dir, file_num, is_save=True):
    all_list = []
    for i in range(0, file_num):
        print("merge_sort_file ->", s_dir + str(i))
        with open(s_dir + str(i) + '.json', 'r') as f:
            all_list += json.loads(f.read())
    if is_save:
        with codecs.open(s_dir + 'all.json', 'w', 'utf-8') as f:
            json.dump(all_list, f, indent=4, sort_keys=True, ensure_ascii=False)
    print("merge_sort_file ->", len(all_list))
    return all_list


# 获取全部坐标
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

# 去除空格和换行
def json_replace(file_data, d_dir_path=None):
    """
    去除空格和换行
    """
    file_str = json.dumps(file_data, separators=(',', ':'), ensure_ascii=False)
    print("json_replace ->", len(file_data))
    file_str.replace('\n', '')
    if d_dir_path:
        with codecs.open(d_dir_path, 'w', 'utf-8') as f:
            f.write(file_str)
    return file_str

# 题库去重
def check_repeat(question_list):
    """
    检查重复
    @return:
    """
    idioms = []
    print("check_repet in  -> ", len(question_list))
    new_list = []
    repet_num = 0
    for val in question_list:
        str_list_1 = val['e'][0].split(',')
        str_list_2 = val['e'][1].split(',')
        str_list_end = val['e'][len(val['e']) - 1].split(',')
        key = str_list_1[3] + ',' + str_list_2[3] + ',' + str_list_end[3]
        if key not in idioms:
            idioms.append(key)
            val['id'] = len(new_list) + 1
            new_list.append(val)
        else:
            repet_num += 1
            # print(key)
            # print(repet_num)
    print("check_repet out -> ", repet_num, len(new_list))
    return new_list


# 检查题目是否在列表中存在
def one_check_repeat(question_list, one_question):
    """
    检查重复
    @return:
    """
    idioms = []
    print("one_check_repeat in  -> ", len(question_list))
    for val in question_list:
        if len(val['e']) < 1:
            continue
        str_list_1 = val['e'][0].split(',')
        str_list_2 = val['e'][1].split(',')
        str_list_end = val['e'][len(val['e']) - 1].split(',')
        key = str_list_1[3] + ',' + str_list_2[3] + ',' + str_list_end[3]
        if key not in idioms:
            idioms.append(key)
    one_question_e_1 = one_question['e'][0].split(',')
    one_question_e_2 = one_question['e'][1].split(',')
    one_question_e_end = one_question['e'][len(one_question['e']) - 1].split(',')
    one_question_key = one_question_e_1[3] + ',' + one_question_e_2[3] + ',' + one_question_e_end[3]
    if one_question_key in idioms:
        print("one_check_repeat out -> ", one_question)
        return True
    else:
        return False


# 获取题库列表差集
def get_difference_list(question_list_1, question_list_2):
    """
    检查重复
    @return:question_list_1剩余
    """
    idioms_1 = []
    idioms_2 = []
    print(len(question_list_1), len(question_list_2))
    for val in question_list_2:
        str_list_1 = val['e'][0].split(',')
        str_list_2 = val['e'][1].split(',')
        str_list_end = val['e'][len(val['e']) - 1].split(',')
        key = str_list_1[3] + ',' + str_list_2[3] + ',' + str_list_end[3]
        idioms_1.append(key)

    for val in question_list_1:
        str_list_1 = val['e'][0].split(',')
        str_list_2 = val['e'][1].split(',')
        str_list_end = val['e'][len(val['e']) - 1].split(',')
        key = str_list_1[3] + ',' + str_list_2[3] + ',' + str_list_end[3]
        if key not in idioms_1:
            idioms_2.append(val)
    print("new_list -> ", len(idioms_2))
    return idioms_2

# 统计成语使用次数
def idioms_use_times(question_list):
    """
    统计成语使用次数
    @return:
    """
    idioms = []
    for val in question_list:
        for on_word in val['e']:
            str_list = on_word.split(',')
            idioms.append(str_list[3])
    print("idioms_use_times idioms->", len(idioms))
    _d = Counter(idioms)
    idiom_num_l = sorted(_d.items(), key=lambda x: x[1], reverse=True)
    print("idioms_use_times idiom_num_l->", len(idiom_num_l))
    return idiom_num_l

# 获取整个题目成语出现频率总和
def question_all_idim_use_times(question, idiom_use_num_d):
    """
    获取整个题目成语出现次数总和
    @return:
    """
    all_use_times = 0
    for one_e in question['e']:
        str_list = one_e.split(',')
        num = idiom_use_num_d.get(str_list[3], 0)
        all_use_times += num
    return all_use_times

# 删除使用相同成语过多的题目
def del_too_many_use(question_list, idioms_limit):
    use_map = {}
    new_list = []
    print("del_too_many_use in ->", len(question_list), idioms_limit)
    for val in question_list:
        is_del = False
        idioms = []
        for on_word in val['e']:
            str_list = on_word.split(',')
            idioms.append(str_list[3])
            if str_list[3] not in use_map:
                use_map[str_list[3]] = 0
            if use_map[str_list[3]] >= idioms_limit:
                is_del = True
                break
        if not is_del:
            for idiom in idioms:
                use_map[idiom] += 1
            val['id'] = len(new_list) + 1
            new_list.append(val)

    print("del_too_many_use out ->", len(new_list))
    return new_list

# 去除含有某些词的题
def del_include_some_idioms(question_list, del_idioms):
    """
    去除含有某些词的题
    @return:
    """
    print("del_include_some_idioms in -> ", len(question_list), del_idioms)
    # 没有要删除的成语
    if len(del_idioms) <= 0:
        return question_list
    # 删除给定成语
    new_list = []
    for val in question_list:
        is_del = False
        for val_e in val['e']:
            str_list = val_e.split(',')
            if str_list[3] in del_idioms:
                is_del = True
                break
        if not is_del:
            new_list.append(val)
    print("del_include_some_idioms out -> ", len(new_list))
    return new_list

# 获取偏僻题数量
def get_pianpi_num(question, r=True):
    """
    获取偏僻题数量
    @return:
    """
    with open(pianpi_file_name + '.json', 'r') as f:
        pianpi = json.loads(f.read())
    pianpi_num = 0
    idiom_num = len(question['e'])
    for on_word in question['e']:
        str_list = on_word.split(',')
        if str_list[3] in pianpi:
            pianpi_num += 1
    # 特殊需求排序
    if r:
        r = float('%.3f' % random.uniform(0, 0.03)) + float(pianpi_num / idiom_num)
        return r
    else:
        return pianpi_num

# 筛选出成语数量和偏僻词数量相等的题目
def get_limit_idioms_num(question_list, idiom_num, pianpi_num = -1):
    """
    筛选出成语数量和偏僻词数量相等的题目
    @param question_list: 题目列表
    @param idiom_num: 限定成语数量
    @param pianpi_num: 偏僻词数量
    @return: 满足需求的列表
    """
    new_list = []
    print("get_limit_idioms_num in->", len(question_list))
    for question in question_list:
        if len(question['e']) == idiom_num:
            if pianpi_num >= 0:
                pianpi = get_pianpi_num(question, False)
                if pianpi == pianpi_num:
                    new_list.append(question)
            else:
                new_list.append(question)
    print("get_limit_idioms_num out->", len(new_list))
    return new_list


# 统计题目行列和
def get_question_max_x_y(question):
    """
    统计题目行列和
    """
    max_x, max_y = 0, 0
    for on_word in question['e']:
        str_list = on_word.split(',')
        if str_list[2] == 'H':
            max_x = max(max_x, int(str_list[0]) + len(str_list[3]))
            max_y = max(max_y, int(str_list[1]) + 1)
        else:
            max_x = max(max_x, int(str_list[0]) + 1)
            max_y = max(max_y, int(str_list[1]) + len(str_list[3]))
    max_x_y = max_x + max_y
    if max_x_y > 18:
        print("max_x_y > 18")
    return max_x_y

# 按行列和筛选
def filter_max_x_y(question_list, limit_x_y):
    """
    筛选合适的行列之和的题目
    """
    print("filter_max_x_y ->", len(question_list), limit_x_y)
    new_list = []
    for val in question_list:
        if get_question_max_x_y(val) <= limit_x_y:
            val['id'] = len(new_list) + 1
            new_list.append(val)
    print("filter_max_x_y ->", len(new_list))
    return new_list


# 按行列相加排序
def sort_min_x_y(question_list):
    """
    按行列相加排序
    @return:
    """
    print("sort_min_x_y in ->", len(question_list))
    new_list = sorted(question_list, key=get_question_max_x_y)
    print("sort_min_x_y out ->", len(new_list))
    return new_list

# 按偏僻词数量排序
def sort_pianpi_num(question_list):
    """
    按偏僻词数量排序
    @return:
    """
    print(len(question_list))
    new_list = sorted(question_list, key=get_pianpi_num)
    print(len(new_list))
    return new_list


# 调整重心
def question_center_pos(question_list):
    """
    重心微调
    @return:
    """
    new_list = []
    for val in question_list:
        new_list.append(one_question_pos(val))
    return new_list

# 获取题目在成语列表出现的成语数量
def include_idioms_num(question, idioms):
    """
    获取题目包含给定成语的数量
    """
    include_num = 0
    for val in question['e']:
        str_list = val.split(',')
        if str_list[3] in idioms:
            include_num += 1
    return include_num


# 疏散相同成语分布
def evacuate_same_idiom(question_list):
    """
    疏散相同成语分布
    """
    max_distance = 5
    change_times = 0  # 移动次数
    cul_index = 0
    while 1:
        idiom_d = {}
        for index, val in enumerate(question_list):
            change_distance = 0
            new_idiom_d = {}
            for on_word in val['e']:
                str_list = on_word.split(',')
                new_idiom_d[str_list[3]] = index
                if (str_list[3] in idiom_d) and (index - idiom_d[str_list[3]] < max_distance):
                    change_distance = max(change_distance, (index + max_distance))
            # 是否移动
            if change_distance > 0:
                if change_distance >= len(question_list):
                    break
                p = val
                question_list[index] = question_list[change_distance]
                question_list[change_distance] = p
                change_times += 1
            else:
                for key, val in new_idiom_d.items():
                    idiom_d[key] = val
            if index >= len(question_list)-4:
                return question_list
            cul_index = index

        print(cul_index)

# 过滤给定id的题库
def del_some_id(question_list, id_list):
    """
    删除给定id的题目
    @return:
    """
    new_list = []
    for index, val in enumerate(question_list):
        if val['id'] not in id_list:
            val['id'] = len(new_list) + 1
            new_list.append(val)
    print("del_some_id out ", len(new_list))
    return new_list

# 判断是否有交集
def is_pos_include(some_pos, all_pos):
    for pos in some_pos:
        if pos in all_pos:
            return True
    return False

# 判断 边长 > 1,面积 > 8 的矩形
def is_space_reach(question):
    """
    判断是否空格过多
    return：true 满足空格要求， false 不满足空格要求
    """

    all_pos = get_all_pos(question['e'])
    max_x, max_y = 0, 0
    for on_word in question['e']:
        str_list = on_word.split(',')
        if str_list[2] == 'H':
            max_x = max(max_x, int(str_list[0]) + len(str_list[3]))
            max_y = max(max_y, int(str_list[1]) + 1)
        else:
            max_x = max(max_x, int(str_list[0]) + 1)
            max_y = max(max_y, int(str_list[1]) + len(str_list[3]))
    if max_x < 5 or max_y < 5:
        return True
    # 左上角坐标
    left_top = ['0_0', '0_1', '0_2', '1_0', '1_1', '1_2', '2_0', '2_1', '2_2']
    if not is_pos_include(left_top, all_pos):
        return False

    # 右上角
    right_top = [
        str(max_x-1)+'_0', str(max_x-1)+'_1', str(max_x-1)+'_2',
        str(max_x-2)+'_0', str(max_x-2)+'_1', str(max_x-2)+'_2',
        str(max_x-3)+'_0', str(max_x-3)+'_1', str(max_x-3)+'_2'
    ]
    if not is_pos_include(right_top, all_pos):
        return False

    # 左下角
    left_bottom = [
        '0_'+str(max_y-1), '1_'+str(max_y-1), '2_'+str(max_y-1),
        '0_'+str(max_y-2), '1_'+str(max_y-2), '2_'+str(max_y-2),
        '0_'+str(max_y-3), '1_'+str(max_y-3), '2_'+str(max_y-3)
    ]
    if not is_pos_include(left_bottom, all_pos):
        return False

    # 右下角
    right_bottom = [
        str(max_x-3)+'_'+str(max_y-1), str(max_x-2)+'_'+str(max_y-1), str(max_x-1)+'_'+str(max_y-1),
        str(max_x-3)+'_'+str(max_y-2), str(max_x-2)+'_'+str(max_y-2), str(max_x-1)+'_'+str(max_y-2),
        str(max_x-3)+'_'+str(max_y-3), str(max_x-2)+'_'+ str(max_y-3), str(max_x-1)+'_'+str(max_y-3)
    ]
    if not is_pos_include(right_bottom, all_pos):
        return False

    # 左上右下
    left_top_and_right_bottom = [
        '0_0', '1_0', '2_0', '3_0',
        '0_1', '1_1', '2_1', '3_1',
        str(max_x-1)+'_'+str(max_y-1), str(max_x-2)+'_'+str(max_y-1), str(max_x-3)+'_'+str(max_y-1), str(max_x-4)+'_'+str(max_y-1),
        str(max_x-1)+'_'+str(max_y-2), str(max_x-2)+'_'+str(max_y-2), str(max_x-3)+'_'+str(max_y-2), str(max_x-4)+'_'+str(max_y-2),
    ]
    if not is_pos_include(left_top_and_right_bottom, all_pos):
        return False

    # 左下右上
    left_bottom_and_right_top = [
        '0_' + str(max_y - 1), '1_' + str(max_y - 1), '2_' + str(max_y - 1), '3_' + str(max_y - 1),
        '0_' + str(max_y - 2), '1_' + str(max_y - 2), '2_' + str(max_y - 2), '3_' + str(max_y - 2),
        str(max_x - 1) + '_0', str(max_x - 2) + '_0', str(max_x - 3) + '_0', str(max_x - 4) + '_0',
        str(max_x - 1) + '_1', str(max_x - 2) + '_1', str(max_x - 3) + '_1', str(max_x - 4) + '_1',
    ]
    if not is_pos_include(left_bottom_and_right_top, all_pos):
        return False

    return True
# 统计不同成语个数的题量
def idiom_num_dict(question_list):
    """
    统计不同成语个数的题量
    @return:
    """
    d = {}
    for val in question_list:
        if str(len(val['e'])) not in d:
            d[str(len(val['e']))] = 0
        d[str(len(val['e']))] += 1
    return d

# 统计全部成语
def get_all_idioms(question_list, file_name=None):
    """
    获取题库全部成语
    @return:
    """
    idioms = []
    for question in question_list:
        for on_word in question['e']:
            str_list = on_word.split(',')
            idioms.append(str_list[3])
    idioms = list(set(idioms))
    if file_name:
        with codecs.open(file_name, 'w', 'utf-8') as f:
            json.dump(idioms, f, indent=4, sort_keys=True, ensure_ascii=False)

    print("get_all_idioms ->", len(idioms))
    return idioms

# 统计全部成语，不去重
def get_all_idioms_no_set(question_list):
    """
    获取题库全部成语
    @return:
    """
    idioms = []
    for question in question_list:
        for on_word in question['e']:
            str_list = on_word.split(',')
            idioms.append(str_list[3])
    return idioms
# 成语库分类
def different_idioms(idioms):
    """
    成语区分成3类：常见，消极，偏僻
    """
    changjian = []
    xiaoji = []
    pianpi = []

    for index, val in enumerate(idioms):
        if val['del'] == 1:
            continue
        if val['comment'] == 1 and val['jiji'] == 1:
            changjian.append(val['idiom'])
        if val['comment'] == 1 and val['jiji'] == 0:
            xiaoji.append(val['idiom'])
        if val['comment'] == 0:
            pianpi.append(val['idiom'])
    return changjian, pianpi, xiaoji

# 题库排序Id
def sort_id(question_list, start=1):
    """
    排列id
    @return:
    """
    question_id = 0 + start
    for index, val in enumerate(question_list):
        question_list[index]['id'] = question_id
        question_id += 1
    return question_list

# 获取固定偏僻词数量的题
def get_pianpi_pro(question_list, p_num=4):
    """
    获取固定偏僻词数量的题
    """
    new_list = []
    with open(pianpi_file_name + '.json', 'r') as f:
        pianpi = json.loads(f.read())
    for index, val in enumerate(question_list):
        print(index)
        pianpi_num = 0
        for on_word in val['e']:
            str_list = on_word.split(',')
            if str_list[3] in pianpi:
                pianpi_num += 1
        if pianpi_num == p_num:
            val['id'] = len(new_list) + 1
            new_list.append(val)
    print(len(new_list))
    return new_list

# 按偏僻字数量分类
def different_by_pianpi_num(question_list, save_dir):
    """
    按偏僻字数量分类
    @return:
    """
    pianpi_d = {}
    for index, question in enumerate(question_list):
        pianpi_num = get_pianpi_num(question, False)
        if str(pianpi_num) not in pianpi_d:
            pianpi_d[str(pianpi_num)] = []
        pianpi_d[str(pianpi_num)].append(question)
    for pianpi_num, pianpi_num_list in pianpi_d.items():
        print("different_by_idioms_num pianpi_num", pianpi_num, len(pianpi_num_list))
        with codecs.open(save_dir + 'pianpi_' + pianpi_num + '.json', 'w', 'utf-8') as f:
            json.dump(pianpi_num_list, f, indent=4, sort_keys=True, ensure_ascii=False)

# 按成语数量分类
def different_by_idioms_num(question_list, save_dir, pianpi_save_dir, is_pianpi_different=False):
    """
    按成语数量分类
    @return:
    """
    print("different_by_idioms_num in ->", len(question_list))
    idioms_num_d = {}
    for index, val in enumerate(question_list):
        key = str(len(val['e']))
        if key not in idioms_num_d:
            idioms_num_d[key] = []
        val['id'] = len(idioms_num_d[key]) + 1
        idioms_num_d[key].append(val)

    for idiom_num, q_list in idioms_num_d.items():
        print("different_by_idioms_num idiom_num", idiom_num, len(q_list))
        with codecs.open(save_dir + idiom_num + '_' + str(len(q_list)) + '.json', 'w', 'utf-8') as f:
            json.dump(q_list, f, indent=4, sort_keys=True, ensure_ascii=False)
        # 按偏僻字分类
        if is_pianpi_different:
            panpi_save_dir = pianpi_save_dir + idiom_num + '_'
            different_by_pianpi_num(q_list, panpi_save_dir)
            # pianpi_d = {}
            # for index, question in enumerate(q_list):
            #     pianpi_num = get_pianpi_num(question, False)
            #     if str(pianpi_num) not in pianpi_d:
            #         pianpi_d[str(pianpi_num)] = []
            #     pianpi_d[str(pianpi_num)].append(question)
            # for pianpi_num, pianpi_num_list in pianpi_d.items():
            #     print("different_by_idioms_num pianpi_num", pianpi_num, len(pianpi_num_list))
            #     with codecs.open(pianpi_save_dir + idiom_num + '_' + 'pianpi_' + pianpi_num + '.json', 'w', 'utf-8') as f:
            #         json.dump(pianpi_num_list, f, indent=4, sort_keys=True, ensure_ascii=False)
    return idioms_num_d

# 部分题目插入题库
def add_question(start_id, s_question_list, add_question_list):
    """
    部分题目插入题库
    :param start_id: 插入位置
    :param s_question_list: 源题库
    :param add_question_list: 插入题目
    :return:
    """
    start_list = s_question_list[0:start_id]
    mid_list = add_question_list
    last_list = s_question_list[start_id:]
    new_list = start_list + mid_list + last_list
    new_list = sort_id(new_list)
    return new_list

# 拆分文件100题1个文件
def split_file(question_list, d_dir=ready_split_dir, step=100, start=0):
    """
    拆分文件
    @return:
    """
    new_idiom = question_list
    # for index, val in enumerate(question_list):
    #     new = {
    #         'id': start + index + 1,
    #         'e': val['e']
    #     }
    #     new_idiom.append(new)

    split_list = [new_idiom[i:i + step] for i in range(0, len(new_idiom), step)]
    for index, val in enumerate(split_list):
        print(index+start, len(val))
        with codecs.open(d_dir + 'tiku_' + str(index + start) + '.json', 'w', 'utf-8') as f:
            json.dump(val, f, indent=4, sort_keys=True, ensure_ascii=False)

# 统计id之前的成语数量
def sort_id_idiom_num(question_list):
    """
    id之前的成语数量
    @return:
    """
    idioms = []
    _d = {}
    tiku_list = sorted(question_list, key=lambda _d: _d['id'])
    for val in tiku_list:
        for e_str in val['e']:
            s_to_l = e_str.split(',')
            idioms.append(s_to_l[3])
        idioms_num = len(list(set(idioms)))
        _d[str(val['id'])] = idioms_num
        print("sort_id_idiom_num", str(val['id']),  idioms_num)
    return _d

# 扩充简繁映射
def add_jt_to_ft_map(jt_idioms, ft_idioms, jt_ft_idiom):

    print(len(jt_idioms), len(ft_idioms), len(jt_ft_idiom))
    _d = {}
    for index, val in enumerate(jt_idioms):
        jt_ft_idiom[val] = ft_idioms[index]
    print(len(jt_ft_idiom))
    return jt_ft_idiom


# 题目加入到储备题库
def question_add_store_tiku(question_list):
    print("question_add_store_tiku in ", len(question_list))
    for question in question_list:
        pianpi_num = get_pianpi_num(question, False)
        idiom_num = len(question['e'])
        file_name = store_dir + str(idiom_num) + '/' + str(idiom_num) + '_pianpi_' + str(pianpi_num) + '.json'
        with open(file_name, 'r') as f:
            store_list = json.loads(f.read())
        store_list.append(question)
        with codecs.open(file_name, 'w', 'utf-8') as f:
            json.dump(store_list, f, indent=4, sort_keys=True, ensure_ascii=False)
    print("question_add_store_tiku end")


def is_like_idoms(question):
    with open(jinyi_file_name, 'r') as f:
        jinyi = json.loads(f.read())
    with open(wulong_file_name, 'r') as f:
        wulong = json.loads(f.read())

    jinyi_id = []
    wulong_id = []
    for val_e in question['e']:
        s_to_l = val_e.split(',')
        if s_to_l[3] in jinyi:
            jinyi_id.append(jinyi[s_to_l[3]])
        if s_to_l[3] in wulong:
            wulong_id.append(wulong[s_to_l[3]])

    if len(list(set(jinyi_id))) != len(jinyi_id):
        return False
    if len(list(set(wulong_id))) != len(wulong_id):
        return False
    return True
