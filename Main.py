# Main.py
import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters
from bytez import Bytez

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BYTEZ_API_KEY = os.getenv("BYTEZ_API_KEY")
PORT = int(os.getenv("PORT", "10000"))  # Render автоматты түрде PORT береді

if not TELEGRAM_TOKEN or not BYTEZ_API_KEY:
    raise RuntimeError("TELEGRAM_TOKEN немесе BYTEZ_API_KEY орнатылмаған!")

bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

sdk = Bytez(BYTEZ_API_KEY)
MODEL_NAME = "openai/gpt-4o"

def start(update: Update, context):
    update.message.reply_text("Сәлем! Мен AI ботпын. Хабар жазыңыз, мен жауап беремін!")

def handle_message(update: Update, context):
    user_text = update.message.text
    model = sdk.model(MODEL_NAME)
    try:
        output = model.run([{"role": "user", "content": user_text}])
        if isinstance(output, dict) and "content" in output:
            reply = output["content"]
        elif isinstance(output, str):
            reply = output
        else:
            reply = str(output)
    except Exception as e:
        reply = f"Қате шықты: {e}"
    update.message.reply_text(reply)

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app = Flask(__name__)

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok", 200

@app.route("/")
def index():
    return "Bot is alive!", 200

if __name__ == "__main__":
    print(f"✅ Flask сервер іске қосылды: порт {PORT}")
    app.run(host="0.0.0.0", port=PORT, threaded=True)