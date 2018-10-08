from pathlib import Path
import csv
from collections import defaultdict
import matplotlib.pyplot as plt

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

# when was the last log
last_log_ts = max([i.last_session for i in collector.values()])

#plotting the distribution of users recency
n, bins, patches = plt.hist([(last_log_ts - i.last_session) / (3600 * 24) for i in collector.values()], 50, normed=1, facecolor='g', alpha=0.75)

plt.xlabel('days')
plt.ylabel('users')
plt.title('recency')
plt.grid(True)
plt.show()

#plotting the distribution of incomes from users
n, bins, patches = plt.hist([i.income for i in collector.values() if i.income > 0 and i.income < 3000], 50, normed=1, facecolor='g', alpha=0.75)

plt.xlabel('money')
plt.ylabel('users')
plt.title('monetary')
plt.grid(True)
plt.show()


#plotting the distribution of users frequency
n, bins, patches = plt.hist([len(i.sessions) for i in collector.values() if len(i.sessions) > 1 and len(i.sessions) < 100], 50, normed=1, facecolor='g', alpha=0.75)

plt.xlabel('sessions')
plt.ylabel('users')
plt.title('frequency')
plt.grid(True)
plt.show()