from pathlib import Path
import csv
from collections import defaultdict
from pprint import pprint

from handlers import parse_line, User, urldecode

from urllib import parse
from collections import Counter

wd = Path.cwd()
data_path = wd / 'data'
file_path = data_path / 'rfm.tsv'


collector = defaultdict(int)
_temp = []
prev_uid = 0

# Finding most popular text queries which had no category
queries = Counter()
with open(file_path, encoding='utf-8', errors='surrogateescape') as f:
    rd = csv.reader(f, delimiter="\t", quotechar='"')
    for line in rd:
        ts, uid, url, geo, hid, money = parse_line(line)
        if 'search.xml' in url:
            if 'text=' in url:
                if 'hid' not in url:
                    if 'page' not in url:
                        params = parse.parse_qs(parse.urlparse(url).query)
                        query_body = params.get('text', '')
                        queries.update(query_body)

pprint(queries.most_common(50))

#calculating an average session revenue for sessions which had a text queries and a defined category
#calculating an average session revenue for sessions which had a text queries and withput a defined category
not_categorized_sessions = []
categorized_sessions = []

for u in collector.values():
    for s in u.sessions:
        if s.used_search and not s.categ_search:
            not_categorized_sessions.append(s.money)
        elif s.used_search and s.categ_search:
            categorized_sessions.append(s.money)

not_categorized_sessions.sort()
categorized_sessions.sort()

for i in range(1, 10):
    print(i / 10, not_categorized_sessions[int(len(not_categorized_sessions) * i / 10)], categorized_sessions[int(len(categorized_sessions) * i / 10)])

