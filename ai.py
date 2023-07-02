import os
import openai

from flask import request, session, g
from util import warp_resp
from db import db

default_module = 'text-davinci-003'
chat_model = 'gpt-3.5-turbo'
edit_model = 'text-davinci-edit-001'
admin_auth_key = os.getenv('AUTH_KEY')
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
        return warp_resp("当前用户使用额度已经用完，请联系管理员five3@163.com")

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

    return warp_resp(call_gpt(messages, 0, 1000, False))


def chatgpt_chat():
    if not auth():
        return {"code": 10000, "msg": "当前用户使用额度已经用完，请联系管理员five3@163.com"}

    data = request.json
    messages = data.get('messages')
    if not messages:
        return {"code": 10001, "msg": "提示词为空"}

    temperature = data.get('temperature', 0)
    if temperature < 0 or temperature > 1:
        temperature = 0

    max_tokens = data.get('max_tokens', 2000)
    if max_tokens > 2000:
        max_tokens = 2000

    return warp_resp({"code": 0, "msg": "执行成功", "data": call_gpt(messages, temperature, max_tokens)})


def call_gpt(messages, temperature, max_tokens, use_markdown=True):
    if use_markdown:
        messages[-1]['content'] += '。以markdown格式返回内容'
    response = openai.ChatCompletion.create(
        model=chat_model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    db.decr(g.bearer)

    return response["choices"][0]["message"]['content'].strip()


def call_gpt_stram():
    response = openai.ChatCompletion.create(
        model=chat_model,
        messages=[{"role": "user", "content": '中国56个民族的名字'}],
        temperature=0.0,
        max_tokens=500,
        stream=True,
        timeout=3
    )
    for chunk in response:
        chunk_message = chunk["choices"][0]['delta']
        print(chunk_message, end='')


def ai_login(data):
    username = data.get('username')
    password = data.get('password')

    user = db.query_user(username)

    if not user:
        return False

    if user.get('password') != password:
        return False

    session['username'] = username
    session['auth_key'] = user.get('auth_key')

    return True


def ai_signup(data):
    username = data.get('username', '')
    password = data.get('password', '')

    if not (username.strip() or password.strip()):
        return False, '用户名、密码不合规'

    if db.query_user(username):
        return False, '邮箱已注册'

    ip = get_ip()
    if db.query_reg_ip(ip):
        return False, '该ip已注册'

    auth_key = db.signup(username, password, ip)
    session['username'] = username
    session['auth_key'] = auth_key

    return True, '注册成功'


def get_bearer():
    bearer = None
    auth_txt = request.headers.get('Authorization')
    if auth_txt and auth_txt.startswith('Bearer '):
        bearer = auth_txt.strip().split(' ')[1]

    return bearer


def get_ip():
    ip = request.headers.get('X-Real-Ip')
    if not ip:
        ip = request.remote_addr

    return ip


def auth():
    if auth_bearer():
        return True

    if auth_login():
        return True

    return auth_anonymous()


def auth_bearer(bearer=None):
    if not bearer:
        bearer = get_bearer()

    if bearer:
        g.bearer = bearer
        if bearer == admin_auth_key:  # admin key
            return True
        return db.verify(bearer)

    return False


def auth_login():
    # 获取用户session，获取绑定的auth_key
    bearer = session.get('auth_key')
    return auth_bearer(bearer)


def auth_anonymous():
    # 根据ip来查询使用额度, 匿名用户有20次请求
    ip = get_ip()
    ip_item = db.query_ip(ip)
    bearer = ip_item['auth_key']
    return auth_bearer(bearer)


def active_licence():
    data = request.json or request.form
    key = data.get('licence')
    licence = db.query_licence(key)

    if not licence:
        return {"code": 10000, "success": False, "msg": "当前license无效，请联系管理员five3@163.com"}

    auth_key = session.get('auth_key')
    if not auth_key:
        return {"code": 10000, "success": False, "msg": "当前license无效用户未登录，请先登录"}

    authed = db.active_licence(auth_key, licence)
    if not authed:
        return {"code": 10000, "success": False, "msg": "认证失败"}

    return {"code": 10000, "success": False, "msg": f"激活成功. 当前用户: {session.get('username')}， 剩余次数：{authed['times']}"}


def is_admin():
    bearer = get_bearer()
    if bearer != admin_auth_key:
        return False

    return True


def create_licence():
    count = request.json.get('count', 0)
    if not isinstance(count, int) or count < 1:
        return {"code": 10000, "msg": "参数无效"}

    if not is_admin():
        return {"code": 10000, "msg": "认证失败"}

    licence = db.create_licence(count)
    return {"code": 10000, "data": licence}


def view_db():
    if not is_admin():
        return {"code": 10000, "msg": "认证失败"}

    return db.db


def get_times():
    return db.query_auth_key(session['auth_key']).get('times', 0)
