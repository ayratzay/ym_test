from datetime import datetime
import urllib


def urldecode(str):
  return urllib.parse.unquote(str)


def parse_line(l):
    ts, uid, url, geo, hid, money = l + [1357024691, '-', '-', '-', '-', 0][len(l):]
    ts = int(ts)
    money = int(money)
    return ts, uid, url, geo, hid, money


class Session:

    def __repr__(self):
        _s = datetime.utcfromtimestamp(self.start).strftime("%Y-%m-%d %H:%M:%S")
        _e = datetime.utcfromtimestamp(self.end).strftime("%Y-%m-%d %H:%M:%S")
        return "SESSION {START} - {END} LEN: {LEN}".format(START=_s, END=_e, LEN=self.actions)

    def __init__(self, ts, geo, hid, money, url):

        self.start = ts
        self.end = ts
        self.geos = {geo}
        self.hids = {hid}
        self.money = money
        self.actions = 1
        self.used_search = 0
        self.success_search = 0
        self.parse_url(url)

    def add_action(self, ts, geo, hid, money, url):
        self.end = ts
        self.geos.update([geo])
        self.hids.update([hid])
        self.money += money
        self.actions += 1
        self.parse_url(url)

    def belongs_to_session(self, ts):
        if ts - self.end > 60 * 30:
            return False
        else:
            return True

    def parse_url(self, url):
        if '/search.xml?text=' in url:
            self.used_search = 1
        if '/search.xml?text=' in url and 'page=' in url:
            self.success_search = 1
        if self.used_search == 1 and 'model.xml?modelid=' in url:
            self.success_search = 1

class User:

    def __repr__(self):
        return "USER {UID}".format(UID=self.uid)

    def __init__(self, uid, fs):
        self.uid = uid
        self.sessions = []
        self.first_session = fs
        self.last_session = 0
        self.income = 0
        self.geos = set()
        self.hids = set()

    def add_action(self, ts, geo, hid, money, url):
        if ts < self.first_session:
            self.first_session = ts
        self.last_session = ts
        self.income += money
        self.geos.update([geo])
        self.hids.update([hid])
        if self.sessions:
            s = self.sessions[-1]
            if s.belongs_to_session(ts):
                s.add_action(ts, geo, hid, money, url)
            else:
                self.sessions.append(Session(ts, geo, hid, money, url))
        else:
            self.sessions.append(Session(ts, geo, hid, money, url))
