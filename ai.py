import os
import openai

from app import app
from flask import request, session


chat_model = 'gpt-3.5-turbo'
edit_model = 'text-davinci-edit-001'
auth_key = os.getenv('AUTH_KEY')
message_map = {}
answer_map = {}
app.config['SECRET_KEY'] = os.urandom(16)


@app.route("/api/chatgpt", methods="POST")
def chatgpt():
    if not auth():
        return {"code": 10000, "msg": "当前无权限"}

    data = request.json
    print(data)

    prompt = data.get('prompt').strip()
    if not prompt:
        return {"code": 10001, "msg": "提示词为空"}
    model = data.get('model')

    if model != chat_model:
        return {"code": 10002, "msg": "指定模型无效"}

    temperature = data.get('temperature', 0)
    if temperature < 0 or temperature > 1:
        temperature = 0

    max_tokens = data.get('max_tokens', 100)
    if max_tokens > 1000:
        max_tokens = 1000

    chat_session_id = data.get('chat_session_id', os.urandom(16))

    message_map.setdefault(chat_session_id, []).append({
        'role': 'user',
        'content': prompt
    })

    ans = call_chatgpt(message_map[chat_session_id], model, temperature, max_tokens)

    return {"code": 0, "msg": "执行成功", "data": ans}


def auth():
    auth_txt = request.headers.get('Authorization')
    if auth_txt and auth_txt.startswith('Bearer '):
        auth_txt = auth_txt.strip().split(' ')[1]
        if auth_txt == auth_key:
            return True


def call_chatgpt(message, model='text-davinci-003', temperature=0, max_tokens=100):
    response = openai.Completion.create(
        model=model,
        messages=message,
        temperature=temperature,
        max_tokens=max_tokens
    )

    return response.choices[0].text
