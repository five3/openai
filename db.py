import os
import json
from threading import Thread, Lock

fork_lock = Lock()
sync_flag = 0   # 0: 不同步， 1： 同步


class DB:
    def __init__(self, path):
        self.path = path
        with open(path) as fp:
            self.db = json.load(fp)
        self._auth_keys_ = self.db.get('auth_keys')

    def verify(self, key):
        auth = self._auth_keys_.get(key)
        if auth and auth.get("times", 0) > 0:
            return auth

        return False

    def decr(self, key):
        global sync_flag
        auth = self._auth_keys_.get(key)
        try:
            fork_lock.acquire()
            if auth and auth.get("time", 0) > 0:
                auth['time'] = auth['time'] - 1
                sync_flag = 1
                self.sync_to_file()
        except Exception as e:
            print("执行db加数异常")
        finally:
            fork_lock.release()

    def sync_to_file(self):
        global sync_flag
        while sync_flag:
            with open(self.path, 'w', encoding='utf-8') as fp:
                json.dump(self.db, fp)
            sync_flag = 0


p = os.path.join(os.path.dirname(__file__), "db.json")
db = DB(p)
