from pathlib import Path
import csv
from collections import defaultdict
from collections import Counter
import numpy as np

from handlers import  parse_line, User

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

last_log_ts = max([i.last_session for i in collector.values()])

# categorizing users by recency, frequency and money
for u in collector.values():

    freq = len(u.sessions)
    rec = (last_log_ts - u.last_session) / (3600 * 24)
    mon = u.income
    if rec < 7:
        u.recency = 1
    elif rec < 14:
        u.recency = 2
    elif rec < 28:
        u.recency = 3
    else:
        u.recency = 4

    if freq == 1:
        u.frequncy = 1
    elif freq < 5:
        u.frequncy = 2
    elif freq < 31:
        u.frequncy = 3
    else:
        u.frequncy = 4

    if mon == 0:
        u.monetary = 1
    elif mon < 100:
        u.monetary = 2
    elif mon < 1000:
        u.monetary = 3
    else:
        u.monetary = 4

#printing the most common 30 groups
group_counter = Counter()
for u in collector.values():
    group = '{R}{F}{M}'.format(R=u.recency, F=u.frequncy, M=u.monetary)
    group_counter.update([group])

print(group_counter.most_common(30))
