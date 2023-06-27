import os
import json
from threading import Thread, Lock

fork_lock = Lock()


class DB:
    def __init__(self, path):
        with open(path) as fp:
            self.db = json.load(fp)
        self._auth_keys_ = self.db.get('auth_keys')

    def verify(self, key):
        auth = self._auth_keys_.get(key)
        if auth and auth.get("time", 0) > 0:
            return auth

        return False

    def decr(self, key):
        auth = self._auth_keys_.get(key)
        try:
            fork_lock.acquire()
            if auth and auth.get("time", 0) > 0:
                auth['time'] = auth['time'] - 1

        except Exception as e:
            print("执行db加数异常")
        finally:
            fork_lock.release()


p = os.path.join(os.path.dirname(__file__), "db.json")
db = DB(p)
