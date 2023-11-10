# -*- coding=utf-8  -*-
import json
import codecs


idioms = []
with open("10_pianpi_2.json", 'r') as f:
    idioms += json.loads(f.read())

print(len(idioms))
with codecs.open("10_pianpi_2.json", 'w', 'utf-8') as f:
    json.dump(idioms[0:5000], f, indent=4, sort_keys=True, ensure_ascii=False)

with codecs.open("10_pianpi_2_1.json", 'w', 'utf-8') as f:
    json.dump(idioms[5000:], f, indent=4, sort_keys=True, ensure_ascii=False)
