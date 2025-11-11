# Main.py
import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes
from bytez import Bytez
import asyncio

# --- Environment ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
BYTEZ_API_KEY = os.getenv("BYTEZ_API_KEY")
PORT = int(os.getenv("PORT", 5000))

if not TOKEN or not BYTEZ_API_KEY:
    raise RuntimeError("TELEGRAM_TOKEN немесе BYTEZ_API_KEY орнатылмаған!")

# --- Telegram bot ---
bot = Bot(TOKEN)

# --- Bytez SDK ---
sdk = Bytez(BYTEZ_API_KEY)
MODEL_NAME = "openai/gpt-4o"

# --- Flask ---
app = Flask(__name__)

@app.route("/")
def index():
    return "Bot is alive!"

# --- Синхронды route ---
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)

    # Async функцияларды sync шақыру үшін event loop
    asyncio.run(handle_update(update))

    return "OK", 200

# --- Хабарламаларды өңдеу ---
async def handle_update(update):
    if update.message:
        text = update.message.text

        # /start командасы
        if text == "/start":
            await update.message.reply_text("Сәлем! Мен AI ботпын. Хабарлама жазыңыз 🙂")
            return

        # AI жауап
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

# --- Main ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)