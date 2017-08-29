# IBM Watson Conversationを使って、コピペだけでAIチャットボットを作る

IBM Watson Conversationを使って、知話輪ボットを作成する方法を紹介します。
今回もボットサーバーは構築せず、Azure Functionsを使って、<B>ブラウザ上でコピペだけで開発</B>をします。<br />
作成手順は下記の通りです。
1. 【Watson】IBMのBluemixにログインし、Watson Conversationの利用を開始する
1. 【Azure】Functionsを作成する
1. 【知話輪管理画面】APIトークンを発行する
1. 【Azure】アプリケーション設定から、APIトークン等を環境変数に設定
1. 【Azure】サードパーティーのライブラリをインストール
1. 【Azure】コーディングをする
1. 【知話輪アプリ】アプリから動作確認をする

以下、詳細を説明します。

## 【Watson】IBMのBluemixにログインし、Watson Conversationの利用を開始する
- 下記のサイトからWatson Conversationにログインする。
    - https://watson-conversation.ng.bluemix.net/login
    - IBMのIDがない場合はサインアップをする。（30日程度の無料トライアルができる）
- ログイン後、ガイドに従ってRegionなどを選択し、Watson ConversationのWorkspaces画面を開く。<br />
<img src="../img/watson_conversation_workspaces.png" width="500px" /><br />
- Createボタンを押し、新たなWorkspaceを作成する。
- Workspaceのビルド画面を開くと、Intents, Entities, Dialogというタブが出てくる。<br />
- Intentsがテキストからユーザの意図を認識するためのもので、例文をいくつか登録しておくと、どの意図かを判断できるようになる。<br />
<img src="../img/watson_conversation_build_intents.png" width="500px" /><br />
- Entitiesは金額、日時など文中の重要な要素を認識するためのもので、これは予め幾つかのパターンが準備されている。<br />
<img src="../img/watson_conversation_build_entities.png" width="500px" /><br />
- Dialogは対話の流れを設定するためのもので、あるIntentにマッチしたら、こういう内容を返すとか、次の流れに進むとか、様々なパターンが設定できる。<br />
<img src="../img/watson_conversation_build_dialog.png" width="500px" /><br />
- 左メニューからDeployを選択し、Credentialsを表示する。ここに表示される内容を後のAzure Functionsの環境変数にセットする。<br />
<img src="../img/watson_conversation_deploy_credentials.png" width="500px" /><br />
    - Username, Password, Workspace IDを後に用いる。

## 【Azure】Functionsを作成する
- Microsoft Azureにログインし、ダッシュボードを表示　https://portal.azure.com
- 左のプラスボタン＞Compute＞Function App＞createを選択<br />
<img src="../img/azure_create_function_app.png" width="300px" /><br />
- Functionの名称やリージョンを選択してcreate<br />
<img src="../img/azure_create_function_app_setup.png" width="300px" /><br />
- functions右のプラスボタンからfunctionを作成し、javascriptのサンプルを選択
<img src="../img/azure_select_javascript_sample.png" width="500px" /><br />
- 作成したfunctionを選択し、右上の「</> Get function URL」から、知話輪の管理画面に設定するためのWebhook URLを取得<br />
<img src="../img/azure_get_url.png" width="500px" /><br />

## 【知話輪管理画面】APIトークンを発行する
- 知話輪管理画面にアクセスし、下記の手順でAPIトークンを発行します。
<img src="../img/chiwawa_management_create_bot_for_watson.png" width="500px" /><br />
1. https://[YOUR_COMPANY_ID].chiwawa.one/admin/login　からログイン
1. 「カスタマイズ＞Bot管理（トークン発行）＞新しく作成する」を選択
1. Azure Functionsで発行されたURLをWebhook URLにセット
1. メッセージを投稿するたびにWatsonが動くと邪魔なので、トリガーワードに「ワトソン」と設定する。すると、「ワトソン」という文字列でメッセージを投稿したときだけボットが動くようになる
1. ダイレクトメッセージを利用「する」を選択し、「登録する」ボタンを押す
1. APIトークンとWebhook検証トークンを次章でAzure Functionsの環境変数にセットするためコピー

## 【Azure】アプリケーション設定から、APIトークン等を環境変数に設定
- functionsの概要画面を表示し、「Application settings」をクリック
<img src="../img/azure_functions_overview.png" width="500px" /><br />
- 知話輪のトークンと、Watsonの情報を環境変数にセット
<img src="../img/azure_set_environment_variable.png" width="500px" /><br />

| 環境変数名 | 値 |
|---|---|
| CHIWAWA_API_TOKEN | 知話輪のAPIトークン |
| CHIWAWA_VALIDATION_TOKEN | 知話輪のWebhook検証用トークン |
| WATSON_USER_NAME | WatsonのUsername |
| WATSON_PASSWORD | WatsonのPassword |
| WATSON_WORKSPACE_ID | WatsonのWorkspace ID |

## 【Azure】WatsonのSDKをインストール
- 下記のサイトからコマンドラインツールを立ち上げる。
```
https://Your_APP_NAME.scm.azurewebsites.net/DebugConsole
```
<img src="../img/azure_kudu_install_javascript.png" width="500px" /><br />

- ライブラリをインストールするため、npm initでpackage.jsonを作成する。（New Fileから作成して直接JSONを書いてもよい。）
```
cd D:\home\site\wwwroot\YourFunctionName
npm init
npm install watson-developer-cloud --save
```

## 【Azure】コーディングをする
以下は、知話輪にメッセージが投稿された際に、Watsonに問合せに行き、その回答を知話輪にメッセージとして投稿するという内容。
Watsonの設定をきちんと行っておけば、QAボットやその他の対話ボットが作れる。
下記のコードをAzure Functionsのindex.jsにコピーするだけでボットが完成する。

```.js
/** メイン処理 */
module.exports = function (context, req) {
    context.log('started');

    if (ChiwawaService.isValidRequest(req, context)) {
        let messageText = ChiwawaService.getMessage(req);
        if (messageText) {
            // トリガーワードを設定した場合は、トリガーワードを除去
            messageText = messageText.replace(/^ワトソン/i, "");
        }
        // Watson Conversationサービスに問い合わせ
        WatsonConversationService.askWatson(messageText, (err, httpResponse, intent, answer) => {
            let result = answer;
            if (err) {
                result = "わかりません。";
            }   
            ChiwawaService.sendMessage(ChiwawaService.getCompanyId(req), ChiwawaService.getGroupId(req), result, (err, httpResponse, body) => {});
            context.res = {body: "OK"};
            context.done();
        }, context);
    }
};

/** ワトソン関連の処理 */
var ConversationV1 = require('watson-developer-cloud/conversation/v1');
const WatsonConversationService = {
    askWatson: function(question, callback, context) {
        const processResponse = function(err, response) {
            if (err) {
                if (callback) callback(err, response, "");
                return;
            }

            // Intentを取得
            let intent = "";
            if (0 < response.intents.length) {
                context.log('Detected intent: #' + response.intents[0].intent);
                intent = response.intents[0].intent;
            }

            // 回答を取得
            let answer = "";
            if (0 < response.output.text.length) {
                answer = response.output.text[0];
            }
            if (callback) callback(err, response, intent, answer);
        };

        const conversation = new ConversationV1({
            username: process.env["WATSON_USER_NAME"],
            password: process.env["WATSON_PASSWORD"],
            path: { workspace_id: process.env["WATSON_WORKSPACE_ID"] },
            version_date: '2016-07-11'
        });

        conversation.message({
            input: { text: question }
        }, processResponse);
    }
};

/** 知話輪関連の処理 */
var request = require('request');
const ChiwawaService = {
    /** リクエストの内容をチェック。
     * @param req リクエストオブジェクト
     * @param context（任意） Azure functionsの場合は、contextをセットすると、問題があった際にエラーレスポンスを返し、contextを処理済みにする。
     * @return 問題がある場合はfalseを返す。。 
     */
    isValidRequest: function(req, context) {
        // headerをチェック
        if (!ChiwawaService.privateMethods.isAuthorized(req)) {
            if (context) {
                context.res = {
                    status: 401,
                    body: "Unauthorized request."
                };
                context.log("401: Unauthorized request.");
                context.done();
            }
            return false;
        }
        
        // bodyをチェック
        if (!ChiwawaService.privateMethods.isBodyValid(req)) {
            if (context) {
                context.res = {
                    status: 400,
                    body: "Request body is not valid. Please set a message in the request body."
                };
                context.log("400: Bad request.");
                context.done();
            }
            return false;
        }
        return true;
    },
    /** リクエストから企業IDを取得 */
    getCompanyId: function(req) {
        return req.body.companyId;
    },
    /** リクエストからグループIDを取得 */
    getGroupId: function(req) {
        return req.body.message.groupId;
    },
    /** リクエストからメッセージを取得 */
    getMessage: function(req) {
        return req.body.message.text;
    },
    /** 知話輪にメッセージを送信 */
    sendMessage: function(companyId, groupId, messageText, callback) {
        const baseUrl = `https://${companyId}.chiwawa.one/api/public/v1/groups/${groupId}/messages`;
        const content = {
            'text': messageText
        };
        const headers = {
            'Content-Type': 'application/json',
            'X-Chiwawa-API-Token': process.env["CHIWAWA_API_TOKEN"]
        };
        const options = {
            url: baseUrl,
            headers: headers,
            json: content
        }
        request.post(options, function(err, httpResponse, body){
            if (callback) callback(err, httpResponse, body);
        });
    },
    privateMethods: {
        isAuthorized: function(req) {
            return req.headers['x-chiwawa-webhook-token'] === process.env["CHIWAWA_VALIDATION_TOKEN"];
        },
        isBodyValid: function(req) {
            return req.body && req.body.type && req.body.message;
        },
    }
}
```

## 【知話輪アプリ】アプリから動作確認をする
- 左メニューのプラスボタンからボットユーザを追加する
<img src="../img/chiwawa_app_before_adding_bot_user.png" width="500px" /><br />
- 自分が作成したボット（ChiwawaWatson）を選択する　（※自分が作成したbotが出てこない場合は、知話輪管理画面で、「ダイレクトメッセージ利用」を「する」になっていることを確認してください。）
<img src="../img/chiwawa_app_add_bot_user.png" width="500px" /><br />
- 「ワトソン」で始まるメッセージを投稿するとAIが適当に返事をしてくれる。
<img src="../img/chiwawa_app_watson_bot.png" width="500px" /><br />

以上で、Watson Conversationを用いた知話輪ボットは完成です。

## 参考資料
- [知話輪とは](https://www.chiwawa.one/)
- [知話輪のAPIドキュメント](https://developers.chiwawa.one/api/)
- [Watson Conversationのチュートリアル（英語）](https://console.bluemix.net/docs/services/conversation/getting-started.html#gettingstarted)
- [Watson ConversationのAPIドキュメント（英語）](https://www.ibm.com/watson/developercloud/conversation/api/v1/?node#)
