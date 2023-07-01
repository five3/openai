import os
import json
import uuid
from threading import Thread, Lock

fork_lock = Lock()
sync_lock = Lock()
sync_flag = 0   # 0: 不同步， 1： 同步
sync_running = 0


class DB:
    def __init__(self, path):
        self.path = path
        with open(path) as fp:
            self.db = json.load(fp)
        self._auth_keys_ = self.db.get('auth_keys')
        self._users_ = self.db.get('users')
        self._ip_ = self.db.get('ip')
        self._reg_ip_ = self.db.get('reg_ip')
        self._licence_ = self.db.get('licence')

    def query_user(self, username):
        return self._users_.get(username)

    def query_licence(self, key):
        licence = self._licence_.get(key)
        if licence and licence['enable']:
            return licence
        else:
            return None

    def query_reg_ip(self, key):
        return self._reg_ip_.get(key)

    def query_ip(self, key):
        if key not in self._ip_:    # 新增一个ip、额度为10
            auth_key = str(uuid.uuid1())
            self._auth_keys_[auth_key] = {
                "times": 10
            }
            self._ip_[key] = {
              "auth_key": auth_key
            }
            self.sync_to_file()

        return self._ip_.get(key)

    def query_auth_key(self, key):
        return self._auth_keys_.get(key)

    def active_licence(self, key, licence):
        auth = self._auth_keys_.get(key)
        if not auth:
            return None

        auth['times'] += licence['count']   # 激活
        licence['enable'] = False       # 设置 激活码失效
        self.sync_to_file()

        return auth

    def create_licence(self, count):
        key = str(uuid.uuid1())
        licence = {
            'count': count,
            "enable": True
        }

        self._licence_[key] = licence
        self.sync_to_file()

        return key

    def verify(self, key):
        auth = self._auth_keys_.get(key)
        if auth and auth.get("times", 0) > 0:
            return auth

        return False

    def decr(self, key):
        auth = self._auth_keys_.get(key)
        try:
            fork_lock.acquire()
            if auth and auth.get("times", 0) > 0:
                auth['times'] = auth['times'] - 1
                self.sync_to_file()
        except Exception as e:
            print("执行db加数异常")
        finally:
            fork_lock.release()

    def signup(self, username, password, ip):
        if ip in self._ip_:
            auth_key = self._ip_[ip]['auth_key']
            auth = self._auth_keys_[auth_key]
            auth['times'] += 30
        else:
            auth_key = str(uuid.uuid1())
            self._auth_keys_[auth_key] = {
                'times': 30
            }

        self._users_[username] = {
            'password': password,
            'auth_key': auth_key,
            'reg_ip': ip
        }

        self._reg_ip_[ip] = True
        self.sync_to_file()

        return auth_key

    def sync_to_file(self):
        global sync_flag
        global sync_running

        sync_flag = 1
        if sync_running:
            return

        try:
            sync_lock.acquire()
            while sync_flag:
                sync_flag = 0
                sync_running = 1
                with open(self.path, 'w', encoding='utf-8') as fp:
                    json.dump(self.db, fp, ensure_ascii=False, indent=2)
        except Exception as e:
            print('同步db异常')
        finally:
            sync_running = 0
            sync_lock.release()


p = os.path.join(os.path.dirname(__file__), "db.json")
db = DB(p)
