import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os
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
class UserContext:
    waiting_for_number = False

user_context = {}


# LINE Developersのチャネルシークレットとチャネルアクセストークンを設定
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
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
    if received_text == "車番検索":
        user_id = event.source.user_id
        user_context[user_id] = UserContext()
        user_context[user_id].waiting_for_number = True
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="検索する車番を入力してください：")
        )

    elif received_text.isdigit() and user_context.get(event.source.user_id) and user_context[event.source.user_id].waiting_for_number:
        b = 0
        CarNum = received_text
        courseIDList = ["130","207","058","100","129","149","171","023","153","042","138","145","222","108","010","133","517","516","513","514","386","384","391","224","372","370","392","492","371","405","390","368","377","376","387","383","366","380","491","489","354","337","320","344","040","114","086","164","219","001","532","113","174","034","096","009","144","003","074","190","155","073","098","175","147","168","188","388","375","097","436","438","427","242","238","430","429","426","434","432","523","519","529","518","146","183","526","522","530","515","528","520","524","512","545","546","582","583","584","585"]
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)

        try:
            for a in range(0,len(courseIDList)):          
                LINEurl = "https://notify-api.line.me/api/notify"
                access_token = "SnXJJ67pDX5qKctgQkhqzRqKIQyRkgIZ4sDbdPWTusf"
                token_dic = {'Authorization': 'Bearer ' + access_token}
                url = 'https://transfer.navitime.biz/sotetsu-style-contents/bus-location/stops?courseId=0003400' + courseIDList[a] + '&vehicleId=' + CarNum
                driver.get(url)
                if a == 1:
                    time.sleep(5)
                else:
                    time.sleep(2)
                route = driver.find_element(By.ID, "vehicle-overview-right").text.replace("\n", "")
                if route != "現在走行しているバスはありません。":
                    reply_message = CarNum + 'を' + route + 'で検知しました' + "\n" + url
                    b = 0
                else:
                    b = b+1 
        finally:
            if b == 100:
                reply_message = "検知しませんでした"
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_message)
            )
            driver.quit()

    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="車番検索と入力してください：")
        )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
