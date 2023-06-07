import hashlib
import os

from threading import Thread
from flask import request
from wechat_handler import receive, reply, util


TOKEN = os.getenv('WECHAT_TOKEN')

"""
微信登录请求接口
"""
def login():
    pass


'''
微信公众号关键字恢复回调接口
'''
def verify():
    if request.method == 'GET':
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

    else:
        args = request.args
        data = request.data
        print(f'args: {args}')
        print(f'Handle Post webdata is : {data}')

        try:
            recMsg = receive.parse_xml(data)
            if isinstance(recMsg, receive.Msg) and recMsg.MsgType == 'text':
                toUser = recMsg.FromUserName
                fromUser = recMsg.ToUserName
                content = "消息已收到，正在努力思考中，请稍后！(具体与问答问题的内容长度有关)"
                replyMsg = reply.TextMsg(toUser, fromUser, content)

                Thread(target=deal_with_chatgpt, args=(recMsg,), name=recMsg.MsgId).start()

                return replyMsg.send()
            else:
                print("暂且不处理")
                return "success"
        except Exception as e:
            return e


def deal_with_chatgpt(recMsg):
    print(f"处理用户信息: {recMsg.Content}")

    # TODO: work with recMsg.Content and get result
    result = '已处理的回答'

    util.send_msg_to_user(recMsg, result)
