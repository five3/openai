import os

import openai
from flask import Flask, redirect, render_template, request, url_for
from ai import chatgpt_chat, chatgpt_answer
from wechat import wechat_login, verify

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(16)
openai.api_key = os.getenv("OPENAI_API_KEY")

app.route('/api/chatgpt', methods=['POST'])(chatgpt_chat)
app.route('/api/chatgpt/answer', methods=['GET'])(chatgpt_answer)

app.route('/wechat/login', methods=['POST'])(wechat_login)
app.route('/wechat/verify', methods=['GET', 'POST'])(verify)


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html", result="")


@app.route("/login")
def login():
    return render_template("index.html", result="")


@app.route("/about")
def about():
    return render_template("index.html", result="")


if __name__ == '__main__':
    app.run('0.0.0.0', 80, threaded=True)
