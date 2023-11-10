# -*- coding=utf-8  -*-
import json
import codecs

with open("jieshi_local.json", 'r') as f:
    jieshi_local = json.loads(f.read())

with open("jt_ft_idiom.json", 'r') as f:
    jt_ft_idiom = json.loads(f.read())

with open("idioms.json", 'r') as f:
    idioms = json.loads(f.read())

all_idioms = list(set([key for key, val in jt_ft_idiom.items()] + idioms))
print(len(jt_ft_idiom))

new_d = {}
err_idiom = []
for val in all_idioms:
    new_d[val] = jieshi_local[val]
    #new_d[val] = jieshi_local[key]
    if 'first_char' not in new_d[val]:
        print(val)

print(len(new_d))
# with codecs.open("jieshi_jt.json", 'w', 'utf-8') as f:
#     json.dump(new_d, f, indent=4, sort_keys=True, ensure_ascii=False)

file_str = json.dumps(new_d, separators=(',', ':'), ensure_ascii=False)
print("json_replace ->", len(new_d))
file_str.replace('\n', '')
with codecs.open("jieshi_samall.json", 'w', 'utf-8') as f:
    f.write(file_str)