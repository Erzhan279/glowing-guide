import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from bytez import Bytez

TOKEN = os.environ["TELEGRAM_TOKEN"]
BYTEZ_API_KEY = os.environ["BYTEZ_API_KEY"]
PORT = int(os.environ["PORT"])

sdk = Bytez(BYTEZ_API_KEY)
MODEL_NAME = "openai/gpt-4o"

app = Flask(__name__)

# --- Telegram App ---
application = ApplicationBuilder().token(TOKEN).build()

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Сәлем! Бот қосылды.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
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

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- Flask route ---
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    asyncio.run(application.process_update(update))
    return "OK", 200

@app.route("/")
def index():
    return "Bot is alive!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)