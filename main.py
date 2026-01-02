import os
import tempfile
from datetime import datetime
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent, AudioMessageContent
from dotenv import load_dotenv
from openai import OpenAI
from notion_client import Client

load_dotenv()

app = Flask(__name__)

configuration = Configuration(access_token=os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
notion = Client(auth=os.getenv('NOTION_TOKEN'))
notion_database_id = os.getenv('NOTION_DATABASE_ID')


@app.route("/")
def home():
    return 'Line Bot Server is running!'


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        user_text = event.message.text

        # 檢查是否以 /a 開頭
        if user_text.startswith('/a '):
            # 提取 /a 後面的文字
            content = user_text[3:].strip()

            if not content:
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="請在 /a 後面輸入要摘要的文字")]
                    )
                )
                return

            # 使用 OpenAI 生成摘要
            summary_response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "請為以下內容生成簡短的摘要，用繁體中文回答，限制在 50 字以內。"},
                    {"role": "user", "content": content}
                ],
                temperature=0.7,
                max_tokens=100
            )

            summary_text = summary_response.choices[0].message.content

            # 取得當前時間
            current_time = datetime.now().isoformat()

            # 存到 Notion
            notion.pages.create(
                parent={"database_id": notion_database_id},
                properties={
                    "名稱": {
                        "title": [
                            {
                                "text": {
                                    "content": f"文字摘要 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                                }
                            }
                        ]
                    },
                    "內容": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": content
                                }
                            }
                        ]
                    },
                    "摘要": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": summary_text
                                }
                            }
                        ]
                    },
                    "時間": {
                        "date": {
                            "start": current_time
                        }
                    },
                    "類型": {
                        "select": {
                            "name": "文字摘要"
                        }
                    }
                }
            )

            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=f"✅ 已儲存到 Notion\n\n📝 內容：{content}\n\n📋 摘要：{summary_text}")]
                )
            )
        else:
            # 如果不是 /a 開頭，就簡單回應 (echo)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=user_text)]
                )
            )


@handler.add(MessageEvent, message=AudioMessageContent)
def handle_audio_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_blob_api = MessagingApiBlob(api_client)

        message_content = line_bot_blob_api.get_message_content(message_id=event.message.id)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.m4a') as temp_audio:
            temp_audio.write(message_content)
            temp_audio_path = temp_audio.name

        try:
            with open(temp_audio_path, 'rb') as audio_file:
                transcript = openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="zh"
                )

            transcribed_text = transcript.text

            # 使用 OpenAI 生成摘要
            summary_response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "請為以下內容生成簡短的摘要，用繁體中文回答，限制在 50 字以內。"},
                    {"role": "user", "content": transcribed_text}
                ],
                temperature=0.7,
                max_tokens=100
            )

            summary_text = summary_response.choices[0].message.content

            # 取得當前時間
            current_time = datetime.now().isoformat()

            notion.pages.create(
                parent={"database_id": notion_database_id},
                properties={
                    "名稱": {
                        "title": [
                            {
                                "text": {
                                    "content": f"語音訊息 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                                }
                            }
                        ]
                    },
                    "內容": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": transcribed_text
                                }
                            }
                        ]
                    },
                    "摘要": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": summary_text
                                }
                            }
                        ]
                    },
                    "時間": {
                        "date": {
                            "start": current_time
                        }
                    },
                    "類型": {
                        "select": {
                            "name": "語音"
                        }
                    }
                }
            )

            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=f"✅ 已儲存到 Notion\n\n📝 內容：{transcribed_text}\n\n📋 摘要：{summary_text}")]
                )
            )
        finally:
            os.unlink(temp_audio_path)


if __name__ == "__main__":
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
