import os
import requests

token_url = 'https://api.weixin.qq.com/cgi-bin/token'
send_msg_url = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={token}'
app_id = os.getenv('WECHAT_APP_ID')
secret = os.getenv('WECHAT_SECRET')


def get_token(app_id, app_secret):
    args = {
        'grant_type': 'client_credential',
        'appid': app_id,
        'secret': app_secret
    }

    rep = requests.get(token_url, params=args).json()
    print(f'获取token响应：{rep}')

    return rep.get('access_token')


def send_msg_to_user(recMsg, msg):
    token = get_token(app_id, secret)
    url = send_msg_url.format(token=token)

    data = {
        "touser": recMsg.FromUserName,
        "msgtype": "text",
        "text": {
            "content": msg
        }
    }
    rep = requests.post(url, json=data).json()

    print(f'发送消息给用户结果：{rep}')
