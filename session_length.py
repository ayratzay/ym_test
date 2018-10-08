from pathlib import Path
import matplotlib.pyplot as plt


import csv
from time import time

from collections import defaultdict


wd = Path.cwd()
data_path = wd / 'data'
file_path = data_path / 'rfm.tsv'


coll = defaultdict(lambda: {'p': 0, 'f': time(), 'l': 0})

# calculating of users lifespan in service
with open(file_path, encoding='utf-8', errors='surrogateescape') as f:
    rd = csv.reader(f, delimiter="\t", quotechar='"')
    for line in rd:
        ts, uid = int(line[0]), line[1]
        coll[uid]['p'] += 1
        if coll[uid]['f'] > ts:
            coll[uid]['f'] = ts
        if coll[uid]['l'] < ts:
            coll[uid]['l'] = ts


span_hours = [(i['l'] - i['f']) / 3600 for i in coll.values()]

# plotting uf users lifespan in service
plt.hist(span_hours, bins=30)
plt.title("Time using service_hours")
plt.xlabel("hours")
plt.ylabel("users")
plt.show()
