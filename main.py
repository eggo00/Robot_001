import os
import tempfile
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

load_dotenv()

app = Flask(__name__)

configuration = Configuration(access_token=os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


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
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=event.message.text)]
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

            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=transcript.text)]
                )
            )
        finally:
            os.unlink(temp_audio_path)


if __name__ == "__main__":
    app.run(port=8000, debug=True)
