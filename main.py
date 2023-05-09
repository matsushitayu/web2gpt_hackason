import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import openai
import re
import requests
from PIL import Image
from io import BytesIO
from urllib.parse import unquote
import base64


# URLを抽出するための正規表現
url_pattern = re.compile(r'(https?://[\w/:%#@$&?~.=+\-]+)')

# OpenAIのAPIキー
chatgpt_api_key = "sk-＊＊＊＊＊＊＊＊＊"

# FastAPIのインスタンスを作成
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # すべてのオリジンを許可する場合
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DiscordのWebhookのURL
webhook_url = 'https://discord.com/api/webhooks/＊＊＊＊＊＊＊＊＊＊?wait=true'

headers = {
    "Content-Type": "application/json",
    "User-Agent": "DiscordBot (private use) Python-urllib/3.10",
}


# 受け取るJSONの形式を定義
class ChromeExtensionInput(BaseModel):
    text: str
    imageURLs: List[str]
    pageURL: str


# 画像をBytesIOに変換する
def pil_to_byte(img, format="webp"):
    img_bytes = BytesIO()
    img.save(img_bytes, format=format)
    img_bytes = img_bytes.getvalue()
    return img_bytes


# 受け取ったJSONを確認するテスト用API
@app.post("/test/")
async def test(input_data: ChromeExtensionInput):
    print("Received text:", input_data.text)
    print("Received imageURLs:", input_data.imageURLs)
    print("Received pageURL:", input_data.pageURL)
    return {"received_data": input_data}


# 受け取ったJSONで投稿を作成するAPI
@app.post("/make_summary/")
async def make_summary(input_data: ChromeExtensionInput):
    print("リクエストを受け取りました")

    # pageURLが空だったら、https://kadokawa.co.jp/にする
    if input_data.pageURL == "":
        input_data.pageURL = "https://kadokawa.co.jp/"
    # 受け取った画像URLから画像をダウンロードしDiscordのWebhookにアップロードする
    image_urls = [unquote(url) for url in input_data.imageURLs]
    if len(image_urls) > 0:
        print("画像を投稿しています……" + str(len(image_urls)) + "枚")
        for image_url in image_urls:
            print("image_url:", image_url)
            # URLが無効だったらスキップ
            if not url_pattern.match(image_url):
                continue
            image_content = requests.get(image_url).content
            image = Image.open(BytesIO(image_content))
            # 画像をDiscordのWebhookにアップロードする
            string_img = pil_to_byte(image, format="webp")
            files = {"file.webp": string_img}
            image_res = requests.post(webhook_url, json={}, files=files)
            print("image_res:", image_url + str(image_res))

    # 受け取ったテキストをOpenAI APIに投げて、タイトルと本文を作成する
    print("和訳して要約しています……")
    decoded_text = base64.b64decode(input_data.text).decode("utf-8")
    print("input_data.text:", decoded_text)
    openai.api_key = chatgpt_api_key
    summary = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "以下のテキストを1000文字程度の、読みやすい"
                                          "日本語で要約してください。文章には適切に改行を入れ、"
                                          "読みやすくしてください。必ず日本語で御願いいたします。"
                                          "Answer in Japanese."},
            {"role": "user", "content": decoded_text},
        ],
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=0.3
    )
    res = requests.post(webhook_url, json={"content": str(summary.choices[0].message.content)
                                                      +"\n\n"+input_data.pageURL},
                        headers=headers)

    print("res:", res)

    return {"status_code": res.status_code}


