# Main.py
import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from bytez import Bytez

# --- Environment variables ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BYTEZ_API_KEY = os.getenv("BYTEZ_API_KEY")
PORT = int(os.getenv("PORT", 10000))

if not TELEGRAM_TOKEN or not BYTEZ_API_KEY:
    raise RuntimeError("TELEGRAM_TOKEN немесе BYTEZ_API_KEY орнатылмаған!")

# --- Bytez SDK ---
sdk = Bytez(BYTEZ_API_KEY)
MODEL_NAME = "openai/gpt-4o"

# --- Telegram App ---
app_telegram = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# --- Flask App ---
app = Flask(__name__)

# --- /start командасы ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Сәлем! Мен AI ботпын. Хабар жазыңыз, мен жауап беремін!")

# --- Пайдаланушы хабарламасын өңдеу ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    await update.message.reply_text(reply)

# --- Handler-лерді қосу ---
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- Flask webhook маршруты ---
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, app_telegram.bot)
    await app_telegram.process_update(update)
    return "ok", 200

@app.route("/")
def index():
    return "Bot is alive!", 200

if __name__ == "__main__":
    print(f"✅ Flask сервер іске қосылды: порт {PORT}")
    app.run(host="0.0.0.0", port=PORT, threaded=True)