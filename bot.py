from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage
)

app = Flask(__name__)

# LINE Developersのチャネルシークレットとチャネルアクセストークンを設定
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
line_bot_api　= LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # X-Line-Signatureヘッダーの取得
    signature = request.headers['X-Line-Signature']

    # リクエストの取得
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 署名の検証
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 受信したメッセージを取得
    received_text = event.message.text

    # 受信したメッセージをそのまま返信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=received_text)
    )

if __name__ == "__main__":
    app.run()
