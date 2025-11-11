from flask import Flask, request
from telegram import Bot, Update
from telegram.utils.request import Request
from bytez import Bytez
import asyncio
import os

TOKEN = os.environ["TELEGRAM_TOKEN"]
BYTEZ_API_KEY = os.environ["BYTEZ_API_KEY"]
PORT = int(os.environ["PORT"])

request = Request(con_pool_size=20, read_timeout=15, connect_timeout=15)
bot = Bot(token=TOKEN, request=request)

sdk = Bytez(BYTEZ_API_KEY)
MODEL_NAME = "openai/gpt-4o"

app = Flask(__name__)
loop = asyncio.get_event_loop()

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    loop.create_task(handle_update(update))
    return "OK", 200

async def handle_update(update):
    if update.message:
        text = update.message.text
        if text == "/start":
            await update.message.reply_text("Сәлем! Бот қосылды.")
            return
        try:
            model = sdk.model(MODEL_NAME)
            output = model.run([{"role": "user", "content": text}])
            if isinstance(output, dict) and "content" in output:
                reply = output["content"]
            elif isinstance(output, str):
                reply = output
            else:
                reply = str(output)
        except Exception as e:
            reply = f"Қате шықты: {e}"
        await update.message.reply_text(reply)

@app.route("/")
def index():
    return "Bot is alive!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)