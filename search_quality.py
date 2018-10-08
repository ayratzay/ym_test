from pathlib import Path
import csv
from collections import defaultdict
from pprint import pprint

from handlers import parse_line, User



wd = Path.cwd()
data_path = wd / 'data'
file_path = data_path / 'rfm.tsv'


collector = defaultdict(int)
_temp = []
prev_uid = 0

# Reading all lines in log file and creating User-Session constrution
with open(file_path, encoding='utf-8', errors='surrogateescape') as f:
    rd = csv.reader(f, delimiter="\t", quotechar='"')
    for line in rd:
        ts, uid, url, geo, hid, money = parse_line(line)
        if len(_temp) == 0:
            collector[uid] = User(uid, ts)
            _temp = [[ts, uid, url, geo, hid, money]]
            prev_uid = uid
        elif prev_uid == uid:
            _temp.append([ts, uid, url, geo, hid, money])
        else:
            collector[prev_uid] = User(prev_uid, _temp[0][0])
            _temp.sort(key=lambda x: x[0])
            for i in _temp:
                _ts, _uid, _url, _geo, _hid, _money = i
                collector[prev_uid].add_action(_ts, _geo, _hid, _money, _url)
            _temp= [[ts, uid, url, geo, hid, money]]
            prev_uid = uid


# calculating the amount of total search sessions and successful searches for each category
shid = defaultdict(lambda : {'t': 0, 's': 0})
for u in collector.values():
    for s in u.sessions:
        for h in s.hids:
            shid[h]['t'] += s.used_search
            shid[h]['s'] += s.success_search

# calculating earned money for each category
cat_prime = defaultdict(list)
with open(file_path, encoding='utf-8', errors='surrogateescape') as f:
    rd = csv.reader(f, delimiter="\t", quotechar='"')
    for line in rd:
        ts, uid, url, geo, hid, money = parse_line(line)
        if 'click' in url:
            if money > 0:
                cat_prime[hid].append(money)

# printing the success ratio and earned money fpr each category
data = []
for k, v in shid.items():
    if v['t'] > 100:
        if v['s'] / v['t'] < 0.45:
            data.append([k, v['t'], v['s'] / v['t'], sum(cat_prime[k])])

data.sort(key=lambda x: x[2])
pprint(data)

