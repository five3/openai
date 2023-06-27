import os
import openai

from flask import request, session, g
from util import warp_resp
from db import db

default_module = 'text-davinci-003'
chat_model = 'gpt-3.5-turbo'
edit_model = 'text-davinci-edit-001'
auth_key = os.getenv('AUTH_KEY')
message_map = {}
answer_map = {}
turns = []
last_result = ''
text = ''


def chatgpt_answer():
    """
    问答模式
    :return:
    """
    if not auth():
        return warp_resp("当前用户使用额度已经用户，请联系管理员five3@163.com")

    if request.method == 'GET':
        question = request.args.get("question")
        if not question or question.strip() == '':
            return warp_resp("问题不能为空")
        messages = [
            {
                "role": "user",
                "content": question
            }
        ]
    elif request.method == 'POST':
        messages = request.json
    else:
        return ""

    return warp_resp(call_gpt(messages, 0, 1000))


def chatgpt_chat():
    if not auth():
        return {"code": 10000, "msg": "当前用户使用额度已经用户，请联系管理员five3@163.com"}

    data = request.json
    messages = data.get('messages')
    if not messages:
        return {"code": 10001, "msg": "提示词为空"}

    temperature = data.get('temperature', 0)
    if temperature < 0 or temperature > 1:
        temperature = 0

    max_tokens = data.get('max_tokens', 500)
    if max_tokens > 1000:
        max_tokens = 1000

    return {"code": 0, "msg": "执行成功", "data": call_gpt(messages, temperature, max_tokens)}


def call_gpt(messages, temperature, max_tokens):
    response = openai.ChatCompletion.create(
        model=chat_model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    db.decr(g.bearer)

    return response["choices"][0]["message"]['content'].strip()


def auth():
    if auth_bearer():
        return True

    if auth_login():
        return True

    return auth_anonymous()


def auth_bearer():
    auth_txt = request.headers.get('Authorization')
    if auth_txt and auth_txt.startswith('Bearer '):
        bearer = auth_txt.strip().split(' ')[1]
        g.bearer = bearer
        if bearer == auth_key:  # admin key
            return True

        return db.verify(bearer)

    return False


def auth_login():
    # 获取用户session，获取绑定的auth_key
    return False


def auth_anonymous():
    # 根据ip来查询使用额度, 新用户有50次请求
    return False
