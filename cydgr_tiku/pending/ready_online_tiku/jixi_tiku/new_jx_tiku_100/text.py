# -*- coding=utf-8  -*-

import json
import codecs

new_list = []
for i in range(0,20):
    with open("tiku_" + str(i) + '.json', 'r') as f:
        new_list += json.loads(f.read())
print(len(new_list))
with codecs.open("jx_2000.json", 'w', 'utf-8') as f:
    json.dump(new_list, f, indent=4, sort_keys=True, ensure_ascii=False)