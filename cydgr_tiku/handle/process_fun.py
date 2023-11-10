# -*- coding=utf-8  -*-

import json
import codecs
from collections import Counter
import random
import os
import util
import jt_to_ft
import answer
from center_pos import one_question_pos


"""
自己生成的题库再加工！！！！！

统计id之前对应的成语数量: get_study_idioms_num()
简体转成繁体: jt_question_to_ft()
把生成的题库整理分类: pending_to_store()
筛选出备选题目（去除已经选择好的题目）:
按单个条件选出题目:
产生题目流程：
"""

# 统计id之前对应的成语数量
def get_study_idioms_num():
    """
    获取玩到n关，学到n个成语
    """
    s_dir_path = "../pending/ready_online_tiku/tiku_need/new_tiku_100/tiku_j"
    idioms_path = "study_idioms.json"
    # 合并题库
    all_question_list = util.merge_sort_file(s_dir_path, 88)
    # 生成成语库
    util.get_all_idioms(all_question_list, idioms_path)
    # 获取每题累积学习成语
    result = util.sort_id_idiom_num(all_question_list)
    # 文件去空格
    file_str = util.json_replace(result)

    d_dir_path = "idiom_study_idioms.json"
    with codecs.open(d_dir_path, 'w', 'utf-8') as f:
        f.write(file_str)

# 统计id之前对应的成语
def get_study_idioms():
    """
    获取玩到n关，学到n个成语
    """
    s_dir_path = "../pending/online_tiku_jt/"
    # 合并题库
    all_question_list = util.merge_file_dir(s_dir_path)
    print(len(all_question_list))
    # 获取每关成语
    dictionary = {}
    for question in all_question_list:
        idioms = []
        for on_word in question['e']:
            str_list = on_word.split(',')
            idioms.append(str_list[3])
        dictionary[str(question['id'])] = idioms
    print(len(dictionary))
    # 文件去空格
    #file_str = util.json_replace(dictionary)

    d_dir_path = "total_study_idioms.json"
    with codecs.open(d_dir_path, 'w', 'utf-8') as f:
        # f.write(d_dir_path)
        json.dump(dictionary, f, indent=4, sort_keys=True, ensure_ascii=False)

# 简体转成繁体
def jt_question_to_ft():
    """
    简体题库转换成繁体
    @return:
    """
    jt_pending_tiku_dir = "../pending/ready_online_tiku/tiku_need/new_tiku_100/"
    ft_pending_tiku_dir = "../pending/ready_online_tiku/tiku_need/new_tiku_100_ft/"

    jt_pending_tiku_dir = "../pending/ready_online_tiku/jixi_tiku/new_jx_tiku_100/"
    ft_pending_tiku_dir = "../pending/ready_online_tiku/jixi_tiku/new_ft_tiku_100/"

    err_id = []
    for i in range(0, 20):
        filename = jt_pending_tiku_dir + 'tiku_' + str(i) + '.json'
        print(filename)
        with open(filename, 'r') as f:
            jt_question_list = json.loads(f.read())
        ft_question_list = []
        for index, val in enumerate(jt_question_list):
            new_e = jt_to_ft.jt_to_ft(val['e'])
            if not new_e:
                print("jt_question_to_ft no_idiom err", index)
                err_id.append(val['id'])
                return
            else:
                is_equal = jt_to_ft.is_pos_word_equal(new_e)
                if not is_equal:
                    print("jt_question_to_ft is_equal err", index)
                    err_id.append(val['id'])
                    return
                ft_question_list.append({'e': new_e, 'id': val['id']})
        d_filename = ft_pending_tiku_dir + 'tiku_f' + str(i) + '.json'
        with codecs.open(d_filename, 'w', 'utf-8') as f:
            json.dump(ft_question_list, f, indent=4, sort_keys=True, ensure_ascii=False)

    # with codecs.open("err.json", 'w', 'utf-8') as f:
    #     json.dump(err_id, f, indent=4, sort_keys=True, ensure_ascii=False)

# 把生成的题库整理分类
def pending_to_store():
    """
    把生成的题库整理分类
    @return:
    """
    # 1.合并文件夹下的文件
    s_dir = "../pending/stage/befor_meger/"
    d_dir = "../pending/stage/merge_after_and_diff/"
    save_dir = "../pending/stage/merge_after_and_diff/"
    pianpi_save_dir = "../pending/stage/merge_after_and_diff/pianpi/"
    question_list = util.merge_file_dir(s_dir, d_dir, 7000)
    print("-------------------->>merge_file_dir end")
    # 2.题目去重
    question_list = util.check_repeat(question_list)
    print("-------------------->>check_repeat end")

    # 3.按行列从小到大排列
    question_list = util.sort_min_x_y(question_list)
    # 行列和最大值筛选
    #question_list = util.filter_max_x_y(question_list, 17)
    print("-------------------->>sort_min_x_y end")

    # 4.删除使用次数过多的题目
    use_idioms_limit = max(int(len(question_list) / 200), 10)
    question_list = util.del_too_many_use(question_list, use_idioms_limit)
    # # 统计成语使用次数
    # util.idioms_use_times(question_list)
    print("-------------------->>del_too_many_use end")

    # 5.删除含有不合规成语的题目
    del_idioms = [
    u"好好先生",
    u"南郭先生",
    u"东郭先生",
    u"宝马香车"
    ]
    question_list = util.del_include_some_idioms(question_list, del_idioms)
    print("-------------------->>del_include_some_idioms end")

    # 6.去除不能生成繁体的题目
    question_list = jt_to_ft.del_not_to_ft(question_list)
    print("-------------------->>del_not_to_ft end")

    # 7.去除同义词在一个题目中的词
    question_list = filter(util.is_like_idoms, question_list)
    print("-------------------->>del_not_to_ft end")

    # 8.去除空格多的题目
    question_list = filter(util.is_space_reach, question_list)
    print("is_space_reach out", len(question_list))
    print("-------------------->>is_space_reach end ")

    # 8.按成语个数分类（偏僻词个数分类）
    util.different_by_idioms_num(question_list, save_dir, pianpi_save_dir, True)

# 生成剩余题目
def get_store_info():
    """
    生成剩余题目
    @return:
    """
    d_file_name = "../pending/ready_online_tiku/now_tiku_1_600_6600_8600.json"  # 准备去除的题目
    test_dir = "../pending/ready_online_tiku/test/"  # 准备去除的题目
    test_dir_pianpi = "../pending/ready_online_tiku/test/pianpi/"  # 准备去除的题目
    # 把要去除的题目按成语数量和偏僻字数量分类
    with open(d_file_name, 'r') as f:
        d_question_list = json.loads(f.read())
    util.different_by_idioms_num(d_question_list, test_dir, test_dir_pianpi, True)
    # 去出包含的题目
    files = os.listdir(test_dir_pianpi)
    for filename in files:
        s_to_list = filename.split('_')
        idiom_num = s_to_list[0]
        pianpi_num = s_to_list[2]
        store_file_name = "../store/diff_pianpi/" + idiom_num + '/' + idiom_num + '_pianpi_' + pianpi_num
        if not os.path.exists(store_file_name):
            print("no find", store_file_name)
            continue
        with open(test_dir_pianpi + filename, 'r') as f:
            d_question_list = json.loads(f.read())
        with open(store_file_name, 'r') as f:
            s_question_list = json.loads(f.read())
        new_list = util.get_difference_list(s_question_list, d_question_list)
        #剩余列表保存文件
        with codecs.open(store_file_name, 'w', 'utf-8') as f:
            json.dump(new_list, f, indent=4, sort_keys=True, ensure_ascii=False)
        print(store_file_name, len(s_question_list) - len(new_list), len(s_question_list))


# 统计文件中题目数量
def get_store_count():
    """
    统计文件中题目数量
    """
    s_tiku_dir = "../store/diff_pianpi/"
    dirs = os.listdir(s_tiku_dir)
    _d = {}
    for _dir in dirs:
        files = os.listdir(s_tiku_dir + _dir)
        if _dir not in _d:
            _d[_dir] = {}
        for file_name in files:
            with open(s_tiku_dir + _dir + '/' + file_name, 'r') as f:
                d_question_list = json.loads(f.read())
            _d[_dir][file_name] = len(d_question_list)
    with codecs.open('../store/question_count.json', 'w', 'utf-8') as f:
        json.dump(_d, f, indent=4, sort_keys=True, ensure_ascii=False)


# 从题库储备里面生成题库
def get_tiku():
    """
    按需求生成产品需求题库(在整理好的储备题库里挑选)
    @param is_reset:  是否从头开始生成题库
    @return:
    """
    tiku_need_file = "../pending/ready_online_tiku/jixi_tiku/json/need_jx_1601_3600.json"  # 需求文档
    now_tiku_file = "../pending/ready_online_tiku/jixi_tiku/now_tiku_jx_1601_3600.json"  # 现有题库
    recycle_file = "../pending/ready_online_tiku/tiku_need/recycle/now_tiku_4601_6600.json"  # 准备回收的题目
    new_tiku_file = "../pending/ready_online_tiku/jixi_tiku/new_tiku_jx_1601_3600.json"  # 新题库
    new_split_file = "../pending/ready_online_tiku/jixi_tiku/new_jx_tiku_100/"  # 新题库100一个文件
    store_dir = "../store/diff_pianpi_jx/"

    # 需求文件
    with open(tiku_need_file, 'r') as f:
        tiku_need = json.loads(f.read())
    # 当前需求文件的内容
    with open(now_tiku_file, 'r') as f:
        now_tiku = json.loads(f.read())
    now_tiku_d = {str(question['id']): question for question in now_tiku}
    # 按需求生成题目
    no_id = []  # 生成失败的id
    new_tiku_list = []  # 按需求生成的新列表
    reset_list = []  # 要回收的题目列表
    for index_need, one_need in enumerate(tiku_need):
        if one_need['is_reset'] == 0:
            # 保留原有题目
            for id in range(one_need['start_id'], one_need['end_id'] + 1):
                if str(id) in now_tiku_d:
                    new_tiku_list.append(now_tiku_d[str(id)])
                else:
                    new_tiku_list.append({"id": id, "e": []})
                    no_id.append(id)
        else:
            # 生成新的题目，并且回收原题目
            store_file = store_dir + str(one_need['idiom_num']) + '/' + str(one_need['idiom_num']) + '_pianpi_' + str(one_need['pianpi_num']) + '.json'
            with open(store_file, 'r') as f:
                print(store_file)
                store_tiku = json.loads(f.read())
            print("get_tiku store_tiku read->", len(store_tiku))
            # 开始生成题目
            for id in range(one_need['start_id'], one_need['end_id'] + 1):
                print("------------------------id--------------------------", id)
                # 回收题目
                if str(id) in now_tiku_d:
                    # 成语数量和偏僻数量不变，使用该布局
                    now_tiku_pianpi_num = util.get_pianpi_num(now_tiku_d[str(id)], False)
                    now_tiku_idiom_num = len(now_tiku_d[str(id)]['e'])
                    if now_tiku_idiom_num == one_need['idiom_num'] and now_tiku_pianpi_num == one_need['pianpi_num']:
                        new_d = {
                            'id': id,
                            'e': answer.get_answer(now_tiku_d[str(id)]['e'], one_need['hint_average_num'],one_need['hint_type'])
                        }
                        # 重心微调
                        new_d = one_question_pos(new_d)
                        new_tiku_list.append(new_d)
                        continue
                    else:
                        reset_list.append(now_tiku_d[str(id)])
                # 获取全部题目成语出现次数
                new_tiku_idioms = util.get_all_idioms_no_set(new_tiku_list)
                new_tiku_idioms_count_d = Counter(new_tiku_idioms)
                print("get_tiku reserve_idioms_count_d ->", len(new_tiku_idioms_count_d))
                # 按使用次数排序
                store_tiku = sorted(store_tiku, key=lambda v: util.question_all_idim_use_times(v, new_tiku_idioms_count_d))
                # 保证相邻不挨着,获取相邻8个题目的成
                border_idiom = util.get_all_idioms(new_tiku_list[-8:])
                print("get_tiku border_idiom ->", len(border_idiom))
                # 选择题目
                add = 0
                for one_question in store_tiku:
                    # 是否已经选过
                    is_exit = util.one_check_repeat(new_tiku_list, one_question)
                    if is_exit:
                        continue
                    # 是否包含相邻题目
                    include_border_idiom_num = util.include_idioms_num(one_question, border_idiom)
                    if include_border_idiom_num > 0:
                        continue
                    new_d = {}
                    new_d['id'] = id
                    # 答案获取
                    new_d['e'] = answer.get_answer(one_question['e'], one_need['hint_average_num'], one_need['hint_type'])
                    # 重心微调
                    new_d = one_question_pos(new_d)
                    new_tiku_list.append(new_d)
                    store_tiku.remove(one_question)
                    add = 1
                    break
                if add == 0:
                    no_id.append(id)
            with codecs.open(store_file, 'w', 'utf-8') as f:
                json.dump(store_tiku, f, indent=4, sort_keys=True, ensure_ascii=False)
            print("get_tiku store_tiku write->", len(store_tiku))
    new_tiku_list = sorted(new_tiku_list, key=lambda val:val['id'])
    with codecs.open(new_tiku_file, 'w', 'utf-8') as f:
        json.dump(new_tiku_list, f, indent=4, sort_keys=True, ensure_ascii=False)
    # 回收新重新生成的题目
    # with codecs.open(recycle_file, 'w', 'utf-8') as f:
    #     json.dump(reset_list, f, indent=4, sort_keys=True, ensure_ascii=False)
    # 拆分成100题1个文件
    util.split_file(new_tiku_list, new_split_file, 100, 16)
    if len(no_id) > 0:
        with codecs.open('no_id.json', 'w', 'utf-8') as f:
            json.dump(no_id, f, indent=4, sort_keys=True, ensure_ascii=False)
    print("get_tiku ->", len(new_tiku_list))
    print("-----------------end------------------")

# 回收题目
def recycle_question():
    recycle_dir = "../pending/ready_online_tiku/tiku_need/recycle/"
    files = os.listdir(recycle_dir)
    for file in files:
        with open(recycle_dir + file, 'r') as f:
            question_list = json.loads(f.read())
        util.question_add_store_tiku(question_list)



def split_file():
    new_split_file = "../pending/ready_online_tiku/tiku_need/new_tiku_100/"  # 新题库100一个文件
    new_list = []
    with open("../pending/ready_online_tiku/tiku_need/new_tiku_601_2600.json", 'r') as f:
        new_list += json.loads(f.read())

    with open("../pending/ready_online_tiku/tiku_need/new_tiku_2601_4600.json", 'r') as f:
        new_list += json.loads(f.read())

    # with open("../pending/ready_online_tiku/tiku_need/new_tiku_jx_3601_6000.json", 'r') as f:
    #     new_list += json.loads(f.read())

    for index, val in enumerate(new_list):
        new_list[index]['id'] = index + 1 + 600

    # with codecs.open("../pending/ready_online_tiku/jixi_tiku/_6000.json", 'w', 'utf-8') as f:
    #     json.dump(new_list, f, indent=4, sort_keys=True, ensure_ascii=False)

    util.split_file(new_list, new_split_file, 100, 6)


def reset_some_id():
    """
    重新生成某些id题目
    @return:
    """
    store_dir = "../store/diff_pianpi/"
    with open("all.json", 'r') as f:
        all_question = json.loads(f.read())
    with open("reset_id_1.json", 'r') as f:
        reset_id = json.loads(f.read())
    new_tiku_list = []
    add_question = []
    no_id = []
    for question in all_question:
        need_file = None
        if question['id'] in reset_id:
            print("-------------------------> id : ", question['id'])
            if question['id'] <= 600:
                need_file = "need_1_600.json"
            if question['id'] > 600 and question['id'] <=  2600:
                need_file = "need_601_2600.json"
            if question['id'] > 2600 and question['id'] <= 4600:
                need_file = "need_2601_4600.json"
            if question['id'] > 4600 and question['id'] <= 6600:
                need_file = "need_4601_6600.json"
            if question['id'] > 6600 and question['id'] <= 8800:
                need_file = "need_6601_8800.json"
            if not need_file:
                print(" err need_file ")
                return
            with open("../pending/ready_online_tiku/tiku_need/json/" + need_file, 'r') as f:
                all_need_data = json.loads(f.read())
            for one_need in all_need_data:
                if question['id'] >= one_need["start_id"] and question['id'] <= one_need["end_id"]:
                    need_data = one_need
                    break
            if not need_data:
                new_tiku_list.append(question)
                continue
            store_file = store_dir + str(need_data['idiom_num']) + '/' + str(need_data['idiom_num']) + '_pianpi_' + str(need_data['pianpi_num']) + '.json'
            with open(store_file, 'r') as f:
                print(store_file)
                store_tiku = json.loads(f.read())
            print("get_tiku store_tiku read->", len(store_tiku))
            # 获取全部题目成语出现次数
            new_tiku_idioms = util.get_all_idioms_no_set(new_tiku_list)
            new_tiku_idioms_count_d = Counter(new_tiku_idioms)
            print("get_tiku reserve_idioms_count_d ->", len(new_tiku_idioms_count_d))
            # 按使用次数排序
            store_tiku = sorted(store_tiku, key=lambda v: util.question_all_idim_use_times(v, new_tiku_idioms_count_d))
            # 保证相邻不挨着,获取相邻8个题目的成
            border_idiom = util.get_all_idioms(new_tiku_list[-8:])
            print("get_tiku border_idiom ->", len(border_idiom))
            # 选择题目
            add = 0
            for one_question in store_tiku:
                # 是否已经选过
                is_exit = util.one_check_repeat(new_tiku_list[-1000:], one_question)
                if is_exit:
                    continue
                # 是否包含相邻题目
                include_border_idiom_num = util.include_idioms_num(one_question, border_idiom)
                if include_border_idiom_num > 0:
                    continue
                new_d = {}
                new_d['id'] = question["id"]
                # 答案获取
                new_d['e'] = answer.get_answer(one_question['e'], need_data['hint_average_num'], need_data['hint_type'])
                # 重心微调
                new_d = one_question_pos(new_d)
                new_tiku_list.append(new_d)
                add_question.append(new_d)
                store_tiku.remove(one_question)
                add = 1
                break
            if add == 0:
                no_id.append((store_file, question["id"]))
                new_tiku_list.append(question)
            else:
                with codecs.open(store_file, 'w', 'utf-8') as f:
                    json.dump(store_tiku, f, indent=4, sort_keys=True, ensure_ascii=False)
        else:
            new_tiku_list.append(question)

    print(len(no_id))
    with codecs.open("no_id.json", 'w', 'utf-8') as f:
        json.dump(no_id, f, indent=4, sort_keys=True, ensure_ascii=False)


    print(len(add_question))
    with codecs.open("add_question.json", 'w', 'utf-8') as f:
        json.dump(add_question, f, indent=4, sort_keys=True, ensure_ascii=False)

    print(len(new_tiku_list))
    with codecs.open("new_tiku_list.json", 'w', 'utf-8') as f:
        json.dump(new_tiku_list, f, indent=4, sort_keys=True, ensure_ascii=False)


get_study_idioms_num()

#jt_question_to_ft()

#get_tiku()

#reset_some_id()

#pending_to_store()

