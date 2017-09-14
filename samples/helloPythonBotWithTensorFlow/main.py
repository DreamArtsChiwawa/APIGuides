import os
import json
import requests
from flask import Flask, request, render_template
import recognize
app = Flask(__name__)
env = os.environ

@app.route('/')
def index():
    # 「templates/index.html」のテンプレートを使う
    # 「message」という変数に"Hello"と代入した状態で、テンプレート内で使う
    return render_template('index.html', message="Hello")

@app.route('/messages', methods=['POST'])
def messages():
    if is_request_valid(request):
        body = request.get_json(silent=True)
        companyId = env['COMPANY_ID']
        msgObj = body['message']
        groupId = env['GROUP_ID']
        messageText = msgObj['text']
        userName = msgObj['createdUserName']
        image = json.loads('[' + messageText + ']')
        # train.pyの学習結果をつかって、画像認識を実施
        result = recognize.predict(image)
        # 予測結果をチャットのメッセージとして送信
        send_message(companyId, groupId, 'たぶん、' + str(result))
        return "OK"
    else:
        return "Request is not valid."

# Check if token is valid.
def is_request_valid(request):
    validationToken = env['CHIWAWA_VALIDATION_TOKEN']
    requestToken = request.headers['X-Chiwawa-Webhook-Token']
    return validationToken == requestToken

# Send message to Chiwawa server
def send_message(companyId, groupId, message):
    url = 'https://{0}.chiwawa.one/api/public/v1/groups/{1}/messages'.format(companyId, groupId)
    headers = {
        'Content-Type': 'application/json',
        'X-Chiwawa-API-Token': env['CHIWAWA_API_TOKEN']
    }
    content = {
        'text': message
    }
    requests.post(url, headers=headers, data=json.dumps(content))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
