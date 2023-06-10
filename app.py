import os

import openai
from flask import Flask, redirect, render_template, request, url_for
from ai import chatgpt, chatgpt_answer
from wechat import login, verify

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(16)
openai.api_key = os.getenv("OPENAI_API_KEY")

app.route('/api/chatgpt', methods=['POST'])(chatgpt)
app.route('/api/chatgpt/answer', methods=['GET'])(chatgpt_answer)
app.route('/wechat/login', methods=['POST'])(login)
app.route('/wechat/verify', methods=['GET', 'POST'])(verify)


@app.route("/", methods=("GET", "POST"))
def index():
    return render_template("index.html", result="")


if __name__ == '__main__':
    app.run('0.0.0.0', 80)
