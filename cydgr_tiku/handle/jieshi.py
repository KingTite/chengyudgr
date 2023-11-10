# -*- coding=utf-8  -*-

import json
import codecs
import requests
from bs4 import BeautifulSoup
import time
from xpinyin import Pinyin
import threadpool
import util

import sys

"""
获取百度汉语和学文汉语解释
"""
reload(sys)
sys.setdefaultencoding('utf8')

all_jieshi = []
all_no_jieshi = []

jt_to_ft_map_path = "../data/jt_ft_idiom.json"  # 简繁体映射表
all_idioms_file = "../pending/jieshi/idiom.json"  # 全部成语词库
jieshi_local = "../pending/jieshi/jieshi_local.json"  # 现有解释库

no_jieshi_file = "../pending/jieshi/no_jieshi_local.json"  # 需要查找释义的成语
jieshi_spide = "../pending/jieshi/jieshi_spide.json"  # 新生成的解释
no_jieshi_all = "../pending/jieshi/no_jieshi_all.json"  # 没找到解释的成语
ft_jieshi_file = "../pending/jieshi/google1.6.5_ft_jieshi.json"  # 繁体成语词库
jt_ft_jieshi_file = "../pending/jieshi/google1.6.5_jt_ft_jieshi.json"  # 全部成语词库


def get_first_char():
    """
    检查是否有 first_char
    :return:
    """
    transform = Pinyin()

    with open("jieshi_local.json", 'r') as f:
        all_word = json.loads(f.read())
    print(len(all_word))
    no = 1
    for key, val in all_word.items():
        py = transform.get_pinyin(val["idiom"][0], tone_marks=True)
        if 'first_char' not in all_word[key]:
            no += 1
        all_word[key]['first_char'] = py[0]
    print(no)
    ft_d_str = util.json_replace(all_word)
    with codecs.open('jieshi_local_1.json', 'w', 'utf-8') as f:
        f.write(ft_d_str)


# 合并简体和繁体解释
def jt_ft_merge():
    """
    合并简繁体文件
    @return:
    """
    with open(jieshi_local, 'r') as f:
        jieshi_d = json.loads(f.read())
    print("jt_ft_merge ", len(jieshi_d))

    with open(ft_jieshi_file, 'r') as f:
        ft_jieshi = json.loads(f.read())
    print("jt_ft_merge ", len(ft_jieshi))

    jieshi_d.update(ft_jieshi)
    print("jt_ft_merge ", len(jieshi_d))

    # 去空格
    jieshi_d_str = util.json_replace(jieshi_d)

    with codecs.open(jt_ft_jieshi_file, 'w', 'utf-8') as f:
        f.write(jieshi_d_str)

# 简体解释生成繁体解释
def key_to_ft():
    """
    key转换成繁体
    """
    with open(jt_to_ft_map_path, 'r') as f:
        jt_to_ft_map = json.loads(f.read())

    with open(jieshi_local, 'r') as f:
        jieshi_d = json.loads(f.read())

    print("key_to_ft -> jieshi_d", len(jieshi_d))
    ft_d = {}
    no_ft = []
    for idiom, val in jieshi_d.items():
        if idiom not in jt_to_ft_map:
            no_ft.append(idiom)
        else:
            # if jt_to_ft_map[idiom] in ft_d:
            #     print("repeat ft", jt_to_ft_map[idiom])
            ft_d[jt_to_ft_map[idiom]] = val
    print("key_to_ft -> ft_d", len(ft_d), len(no_ft))

    # 繁体解释
    ft_d_str = util.json_replace(ft_d)
    with codecs.open(ft_jieshi_file, 'w', 'utf-8') as f:
        f.write(ft_d_str)

    with codecs.open("no_ft.json", 'w', 'utf-8') as f:
        json.dump(no_ft, f, indent=4, sort_keys=True, ensure_ascii=False)

    # 合并简繁体文件
    jt_ft_merge()


def get_no_jieshi_words():
    """
    获取没有本地解释的成语
    @return:
    """
    with open(all_idioms_file, 'r') as f:
        words_list = json.loads(f.read())
    with open(jieshi_local, 'r') as f:
        jieshi_d = json.loads(f.read())

    for key, val in jieshi_d.items():
        if key in words_list:
            words_list.remove(key)

    print("get_no_jieshi_words -> ", len(words_list))
    with codecs.open(no_jieshi_file, 'w', 'utf-8') as f:
        json.dump(words_list, f, indent=4, sort_keys=True, ensure_ascii=False)

def spide_baidu_hanyu(idiom):
    """
    百度汉语释义
    """
    url = "https://hanyu.baidu.com/s?wd=" + idiom + "&device=pc&from=home"
    response = requests.get(url)
    response.encoding = 'utf-8'
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    _d = {
        'idiom': idiom
    }

    # 基本释义
    tab_content = soup.find_all('div', {"class": "tab-content"})
    if not tab_content:
        return None
    if len(tab_content) < 2:
        return None
    tab_content_li = tab_content[1]
    li = tab_content_li.find_all('li')
    if len(li) < 2:
        return None

    # 解释
    if li[0]:
        mean = li[0].text
        _d["mean"] = mean.replace(u"【解释】：","")
    else:
        return None

    # 出处
    if li[1]:
        mean = li[1].text
        _d["source"] = mean.replace(u"【出自】：","")
    else:
        return None
    # 拼音
    pinyin = soup.find('dt', {"class": "pinyin"})
    if pinyin.text:
        p = pinyin.text
        _d["py"] = p[1:-1]
    else:
        return None
    return _d


def spide_baidu(idiom):
    """
    百度成语释义
    """
    url = "https://baike.baidu.com/item/" + idiom
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/"
                  "signed-exchange;v=b3",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"
                      "73.0.3683.86 Safari/537.36"
    }
    params = {
        "timestamp": int(time.time()*1000),
        "rt": True
    }
    response = requests.get(url, params, headers=headers)
    response.encoding = 'utf-8'
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    # 基本释义
    basicInfo_left = soup.find(class_="basicInfo-block basicInfo-left")
    basicInfo_right = soup.find(class_="basicInfo-block basicInfo-right")

    if not basicInfo_left or not basicInfo_right:
        #print(idiom)
        return None
    left_list_dd = basicInfo_left.select("dd")
    left_list_dt = basicInfo_left.select("dt")
    right_list_dd = basicInfo_right.select("dd")
    right_list_dt = basicInfo_right.select("dt")

    # print(basicInfo_left)
    # print(basicInfo_right)

    _d = {}
    _d['idiom'] = idiom
    for index, val in enumerate(left_list_dt):
        #print(val.text)
        if val.text == "出    处":
            _d["source"] = left_list_dd[index].text
        if val.text == "释    义" or val.text == "解    释":
            _d["mean"] = left_list_dd[index].text
        if val.text == "拼    音":
            _d["py"] = left_list_dd[index].text
    # print(_d)
    for index, val in enumerate(right_list_dt):
        #print(val.text)
        if val.text == "出    处":
            _d["source"] = right_list_dd[index].text
        if val.text == "释    义" or val.text == "解    释":
            _d["mean"] = right_list_dd[index].text
        if val.text == "拼    音":
            _d["py"] = right_list_dd[index].text
    #print(_d)
    if ("source" not in _d) or ("mean" not in _d) or ("py" not in _d):
        #print(idiom)
        return None
    else:
        return _d

def spide_xuewen(idiom):
    """
    学文成语释义
    """
    p = Pinyin()
    pinyin = p.get_pinyin(idiom, '')
    url = 'http://liuxuewenshuwang.com/' + pinyin + '.html'
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/"
                  "signed-exchange;v=b3",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"
                      "73.0.3683.86 Safari/537.36"
    }
    #print(url)
    response = requests.get(url, {}, headers=headers)
    response.encoding = 'utf-8'
    html = response.text
    try:
        soup = BeautifulSoup(html, "html.parser")
        #print(soup)
        listbody = soup.find('div', {"class": "listbody"})
        listbody_p = listbody.select("p")
        _d = {}
        _d['idiom'] = idiom
        py = listbody_p[2].get_text().replace(u"成语读音：","")
        py = py.replace('\n', "")
        mean = listbody_p[3].get_text().replace(u"成语解释：","")
        mean = mean.replace('\n', "")
        source = listbody_p[4].get_text().replace(u"成语出处：","")
        source = source.replace('\n', "")
        if py and mean and source:
            _d['py'] = py
            _d['mean'] = mean
            _d['source'] = source
            return _d
        else:
            #print(idiom)
            return None
    except:
        #print(idiom)
        return None


def get_jieshi(idiom):
    _d = spide_baidu_hanyu(idiom) or spide_baidu(idiom) or spide_xuewen(idiom)
    if _d:
        all_jieshi.append(_d)
    else:
        print(idiom)
        all_no_jieshi.append(idiom)
    time.sleep(1)

def l_to_d():
    _d = {}
    for val in all_jieshi:
        _d[val['idiom']] = val
    return _d

def convert(jieshi_d):
    """
    获取成语拼音首字母
    :return:
    """
    transform = Pinyin()
    for key, val in jieshi_d.items():
        py = transform.get_pinyin(val["idiom"][0], tone_marks=True)
        jieshi_d[key]['first_char'] = py[0]
    return jieshi_spide

def threadpool_run():
    """
    线程池请求
    @return:
    """
    with open(no_jieshi_file, 'r') as f:
        words_list = json.loads(f.read())
    pool = threadpool.ThreadPool(8)
    r = threadpool.makeRequests(get_jieshi, words_list)
    [pool.putRequest(req) for req in r]
    pool.wait()
    # list 转 dict
    jieshi_d = l_to_d()
    # 增加首字母拼音
    result = convert(jieshi_d)
    with codecs.open(jieshi_spide, 'w', 'utf-8') as f:
        json.dump(result, f, indent=4, sort_keys=True, ensure_ascii=False)
    with codecs.open(no_jieshi_all, 'w', 'utf-8') as f:
        json.dump(all_no_jieshi, f, indent=4, sort_keys=True, ensure_ascii=False)
    print("-----end---------")



# 获取没有本地解释的成语
#get_no_jieshi_words()
# request解释
# threadpool_run()
# 简体key转繁体
# key_to_ft()
get_first_char()