import os
import openai

from flask import request, session
from util import warp_resp

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
    question = request.args.get("question")
    if not question or question.strip() == '':
        return ""

    response = openai.Completion.create(
        model=default_module,
        prompt=question,
        temperature=0,
        max_tokens=1000
    )

    return warp_resp(response["choices"][0]["text"].strip())


def chatgpt():
    if not auth():
        return {"code": 10000, "msg": "当前无权限"}

    data = request.json
    print(data)

    prompt = data.get('prompt')
    if not prompt or not prompt.strip():
        return {"code": 10001, "msg": "提示词为空"}

    model = data.get('model')
    if not model:
        model = default_module

    temperature = data.get('temperature', 0)
    if temperature < 0 or temperature > 1:
        temperature = 0

    max_tokens = data.get('max_tokens', 100)
    if max_tokens > 1000:
        max_tokens = 1000

    chat_session_id = data.get('chat_session_id', os.urandom(16))

    # message_map.setdefault(chat_session_id, []).append({
    #     'role': 'user',
    #     'content': prompt.strip()
    # })

    ans = call_chatgpt(prompt, model, temperature, max_tokens)

    return {"code": 0, "msg": "执行成功", "data": ans}


def auth():
    auth_txt = request.headers.get('Authorization')
    if auth_txt and auth_txt.startswith('Bearer '):
        auth_txt = auth_txt.strip().split(' ')[1]
        if auth_txt == auth_key:
            return True


def call_chatgpt(prompt, model='text-davinci-003', temperature=0, max_tokens=100):
    global turns
    global last_result
    global text

    prompt = text + "\nHuman: " + prompt
    response = openai.Completion.create(
        model=model,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens
    )

    result = response["choices"][0]["text"].strip()
    last_result = result
    turns += [prompt] + [result]  # 只有这样迭代才能连续提问理解上下文

    if len(turns) <= 10:  # 为了防止超过字数限制程序会爆掉，所以提交的话轮语境为10次。
        text = " ".join(turns)
    else:
        text = " ".join(turns[-10:])

    return result
