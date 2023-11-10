# -*- coding=utf-8  -*-

import json
import codecs

idioms = [
    u"悱恻缠绵",
    u"虎踞龙盘"
]

err_id = []
for i in range(0, 88):
    with open("tiku_j" + str(i) + '.json', 'r') as f:
        jt_question_list = json.loads(f.read())

    for question in jt_question_list:
        for index, e_val in enumerate(question['e']):
            l = e_val.split(",")
            if l[3] in idioms:
                err_id.append(question['id'])
with codecs.open("err_id.json", 'w', 'utf-8') as f:
    json.dump(err_id, f, indent=4, sort_keys=True, ensure_ascii=False)