import os

import openai
from flask import Flask, redirect, render_template, request, url_for
from ai import chatgpt_chat, chatgpt_answer, ai_login, ai_signup, active_licence, create_licence, view_db
from wechat import wechat_login, verify

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(16)
openai.api_key = os.getenv("OPENAI_API_KEY")

app.route('/api/db', methods=['GET'])(view_db)
app.route('/api/create/licence', methods=['POST'])(create_licence)
app.route('/api/active/licence', methods=['POST'])(active_licence)

app.route('/api/chatgpt', methods=['POST'])(chatgpt_chat)
app.route('/api/chatgpt/answer', methods=['GET'])(chatgpt_answer)

app.route('/wechat/login', methods=['POST'])(wechat_login)
app.route('/wechat/verify', methods=['GET', 'POST'])(verify)


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html", result="")


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template("signup.html", msg="")
    else:
        # 注册成功，再返回主页，新用户赠送50次，一个ip只能注册一个
        ret, msg = ai_signup(request.form)
        if not ret:
            return render_template("signup.html", msg=msg)
        return redirect(url_for('index'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html", msg="")
    else:
        # 认证后设置session，再返回主页
        auth = ai_login(request.form)
        if auth:
            return redirect(url_for('index'))
        else:
            return render_template("login.html", msg="认证失败")


@app.route("/about")
def about():
    return render_template("about.html", result="")


if __name__ == '__main__':
    app.run('0.0.0.0', 80, threaded=True)
