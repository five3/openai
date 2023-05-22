import hashlib
import os

from app import app
from flask import request


TOKEN = os.environ.get('WECHAT_TOKEN')

"""
微信登录请求接口
"""
@app.route("/wechat/login", methods=("POST"))
def login():
    pass


'''
微信公众号关键字恢复回调接口
'''
@app.route("/wechat/verify")
def verify():
    try:
        data = request.args
        if len(data) == 0:
            return "hello, this is handle view"

        print(data)
        signature = data.get('signature')
        timestamp = data.get('timestamp')
        nonce = data.get('nonce')
        echostr = data.get('echostr')

        token = TOKEN  # 请按照公众平台官网\基本配置中信息填写

        list = [token, timestamp, nonce]
        list.sort()
        sha1 = hashlib.sha1()
        map(sha1.update, list)
        hashcode = sha1.hexdigest()

        print("handle/GET func: hashcode, signature: ", hashcode, signature)

        if hashcode == signature:
            return echostr
        else:
            return ""

    except Exception as Argument:
        return Argument
