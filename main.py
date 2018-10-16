from pathlib import Path
import csv
from collections import defaultdict
from collections import Counter

from handlers import parse_line, User

wd = Path.cwd()
data_path = wd / 'data'
file_path = data_path / 'rfm.tsv'

# The dict with will gather users data
# dict { USER ID : USER CLASS OBJECT}
collector = defaultdict(int)
_temp = []
prev_uid = 0


# Reading all lines in log file and creating User-Session constrution
with open(file_path, encoding='utf-8', errors='surrogateescape') as f:
    rd = csv.reader(f, delimiter="\t", quotechar='"')
    for line in rd:
        ts, uid, url, geo, hid, money = parse_line(line) # parsing line. If line is missing data, parser fulfills data with '-'
        if len(_temp) == 0:  # check if we parse new users data
            collector[uid] = User(uid, ts) # adding User type object into collector
            _temp = [[ts, uid, url, geo, hid, money]]
            prev_uid = uid
        elif prev_uid == uid:  # check if data comes from existing user
            _temp.append([ts, uid, url, geo, hid, money])
        else:  # last line of existing user was parsed
            collector[prev_uid] = User(prev_uid, _temp[0][0])
            _temp.sort(key=lambda x: x[0])  # sort
            for i in _temp:
                _ts, _uid, _url, _geo, _hid, _money = i
                collector[prev_uid].add_action(_ts, _geo, _hid, _money, _url)
            _temp= [[ts, uid, url, geo, hid, money]]
            prev_uid = uid

payers = [i for i in collector.values() if i.income > 0] # filter out all users who created 0 revenue
total_users = len(payers)
day_in_secs = 60 * 60 * 24

# now we need to calculate frequency of each users sessions with generated revenue
# ex. if user had 4 sessions and only in two sessions the user has generated revenue, we count users frequency as 2
sessions = [len([_s for _s in _i.sessions if _s.money > 0]) for _i in payers] # get number of sessions with clicks for each revenue
sessions.sort()
print(sessions[int(len(sessions) * 0.33)]) # print out 33th percentile
print(sessions[int(len(sessions) * 0.66)]) # print out 66th percentile
# now we can segment all uses on 3 segments based on their frequency

# then we want to segment users on monetary value. Similarly we will separate users on 3 segments based on total generated revenue
# of each user
income = [_i.income for _i in payers]
income.sort()
print(income[int(len(income) * 0.33)]) # print out 33th percentile
print(income[int(len(income) * 0.66)]) # print out 66 percentile


#now we want to know users` lifetime. We will use this number as a hint how we can segment users based on their recency.
for i in range(0, 60):
    val = 0
    for v in payers:
        delta = v.last_session - v.first_session
        val += delta / day_in_secs >= i
    print(i, val / total_users)

# at this point we have decided with each rfm segment limits which are:
# recency 7, 30 and over 30
# frequency of sessions with at least one click 1 3 and over 3
# money 25 110 aover 110

last_log_ts = max([i.last_session for i in collector.values()]) # last log ts

# now we need to label each user who generate revenue accordingly:
for u in payers:
    freq = len([_s for _s in u.sessions if _s.money > 0])
    rec = (last_log_ts - u.last_session) / (3600 * 24)
    mon = u.income
    if rec <= 7:
        u.recency = 1
    elif rec <= 30:
        u.recency = 2
    else:
        u.recency = 3

    if freq == 1:
        u.frequncy = 1
    elif freq <= 3:
        u.frequncy = 2
    else:
        u.frequncy = 3

    if mon <= 25:
        u.monetary = 1
    elif mon < 110:
        u.monetary = 2
    else:
        u.monetary = 3

#printing segments and the number of users in segment
group_counter = Counter()
for u in payers:
    group = '{R}{F}{M}'.format(R=u.recency, F=u.frequncy, M=u.monetary)
    group_counter.update([group])

print(group_counter.most_common(30))
print(len(group_counter))

#printing segments and the amount of generated revenue
group_revenue = defaultdict(int)
for u in payers:
    group = '{R}{F}{M}'.format(R=u.recency, F=u.frequncy, M=u.monetary)
    group_revenue[group] += u.income

print(group_revenue.most_common(30))
