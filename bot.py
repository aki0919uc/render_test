import chromedriver_binary
import datetime
import requests
import re
import json
import time
from bs4 import BeautifulSoup as bs
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
    waiting_for_reset_number = False
user_context = {}

class wholeapp:
    processing = False
w = wholeapp()

# LINE Developersのチャネルシークレットとチャネルアクセストークンを設定
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
access_token = os.getenv('LINE_Notify_token')
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
LINEurl = "https://notify-api.line.me/api/notify"


class dettime:
    dettime1551 = "03:00"
    dettime1552 = "03:00"
d = dettime()
courseIDList = ["130","207","058","100","129","149","171","023","153","042","138","145","222","108","010","133","517","516","513","514","386","384","391","224","372","370","392","492","371","405","390","368","377","376","387","383","366","380","491","489","354","337","320","344","040","114","086","164","219","001","532","113","174","034","096","009","144","003","074","190","155","073","098","175","147","168","188","388","375","097","436","438","427","242","238","430","429","426","434","432","523","519","529","518","146","183","526","522","530","515","528","520","524","512","545","546","582","583","584","585"]


def extract_js_var(soup, js_var):
    script = soup.find('script', string=re.compile(js_var, re.DOTALL))    #scriptタグを検索
    if script is not None:
        regex = '(?:var )' + js_var + '(.*?)' + '(?: = new navitime.geo.overlay.Pin(.*?)({[\s\S]*})(.*?);)' #busPinで検索
        json_str = re.search(regex, script.string).group(1) #最上位(始発に近い)のピンを選択
        if "next" in json_str:
            json_str = json_str.replace('_next','')
        return json.loads(json_str)

def log():
    now = datetime.datetime.now().strftime("%H:%M")
    FMT = "%H:%M"
    td = datetime.timedelta(hours=1, minutes=30)
    timezero = datetime.timedelta(hours=0, minutes=00)
    token_dic = {'Authorization': 'Bearer ' + access_token}


    j = 2
    for a in range(0,len(courseIDList)):
        url_locate = 'https://transfer.navitime.biz/sotetsu/smart/location/BusLocationMap?courseId=0003400'+ courseIDList[a]
        res = requests.get(url_locate)
        
        if __name__ == "__main__":
            html = res.text
            soup = bs(html, 'html.parser')
            td1551 = datetime.datetime.strptime(now,FMT) - datetime.datetime.strptime(d.dettime1551,FMT)
            td1552 = datetime.datetime.strptime(now,FMT) - datetime.datetime.strptime(d.dettime1552,FMT)
            CarNum = extract_js_var(soup, 'busPin')
            url_navi_loc = 'https://transfer.navitime.biz/sotetsu-style-contents/bus-location/stops?courseId=0003400' + courseIDList[a] + '&vehicleId=' + str(CarNum)
            if CarNum == 1551:
                if td1551 > td or td1551 < timezero:
                    message1551 = '1551が動いています。\n' + url_navi_loc
                    payload1551 = {'message': message1551}
                    requests.post(LINEurl, headers=token_dic, data=payload1551,)
                d.dettime1551 = now
            if CarNum == 1552:
                if td1552 > td or td1552 < timezero:
                    message1552 = '1552が動いています。\n' + url_navi_loc
                    payload1552 = {'message': message1552}
                    requests.post(LINEurl, headers=token_dic, data=payload1552,)
                d.dettime1552 = now
            j = j+1
            time.sleep(0.3)

@app.route('/notify', methods=['GET'])
def notify():
    log()
    return'OK'
    

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
        user_context[event.source.user_id].waiting_for_number = False
        user_context[event.source.user_id].waiting_for_reset_number = False
        if w.processing:
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="現在使用中です、しばらく時間を空けてください")
        )
        else:
            w.processing = True
            user_id = event.source.user_id
            user_context[user_id] = UserContext()
            user_context[user_id].waiting_for_number = True
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="検索する車番を入力してください：")
            )

    elif received_text.isdigit() and user_context.get(event.source.user_id) and user_context[event.source.user_id].waiting_for_number:
        user_context[event.source.user_id].waiting_for_number = False
        b = 0
        CarNum = received_text
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)

        try:
            for c in range(0,len(courseIDList)):
                url_navi = 'https://transfer.navitime.biz/sotetsu-style-contents/bus-location/stops?courseId=0003400' + courseIDList[c] + '&vehicleId=' + CarNum
                driver.get(url_navi)
                if c == 1:
                    time.sleep(5)
                else:
                    time.sleep(1)
                route = driver.find_element(By.ID, "vehicle-overview-right").text.replace("\n", "")
                if route != "現在走行しているバスはありません。":
                    reply_message = CarNum + 'を' + route + 'で検知しました' + "\n" + url_navi
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
            w.processing = False
            
    elif received_text == "リセット":
        user_context[event.source.user_id].waiting_for_number = False
        user_id = event.source.user_id
        user_context[user_id] = UserContext()
        user_context[user_id].waiting_for_reset_number = True

    elif received_text.isdigit() and user_context.get(event.source.user_id) and user_context[event.source.user_id].waiting_for_reset_number:
        user_context[event.source.user_id].waiting_for_reset_number = False
        CarNum = received_text
        if CarNum == 1551:
            d.dettime1551 = "03:00"
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="1551をリセットしました")
            )

        if CarNum == 1552:
            d.dettime1552 = "03:00"
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="1552をリセットしました")
            )
    
    else:
        user_context[event.source.user_id].waiting_for_number = False
        user_context[event.source.user_id].waiting_for_reset_number = False
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="車番検索と入力してください：")
        )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
