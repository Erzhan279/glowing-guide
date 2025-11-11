# Main.py
import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters
from bytez import Bytez

# --- Environment variables ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BYTEZ_API_KEY = os.getenv("BYTEZ_API_KEY")
PORT = int(os.getenv("PORT", 5000))  # Render автоматты береді

if not TELEGRAM_TOKEN or not BYTEZ_API_KEY:
    raise RuntimeError("TELEGRAM_TOKEN немесе BYTEZ_API_KEY орнатылмаған!")

# --- Telegram bot және dispatcher ---
bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

# --- Bytez SDK бастау ---
sdk = Bytez(BYTEZ_API_KEY)
MODEL_NAME = "openai/gpt-4o"

# --- /start командасы ---
def start(update: Update, context):
    update.message.reply_text(
        "Сәлем! Мен AI ботпын. Мәтінді жазыңыз, мен жауап беремін."
    )

# --- Пайдаланушы хабарламасын өңдеу ---
def handle_message(update: Update, context):
    user_text = update.message.text
    model = sdk.model(MODEL_NAME)

    try:
        output = model.run([{"role": "user", "content": user_text}])

        # Bytez кейде dict, кейде str қайтарады
        if isinstance(output, dict) and "content" in output:
            reply = output["content"]
        elif isinstance(output, str):
            reply = output
        else:
            reply = str(output)

    except Exception as e:
        reply = f"Қате шықты: {e}"

    update.message.reply_text(reply)

# --- Handlers қосу ---
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- Flask app ---
app = Flask(__name__)

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok", 200

@app.route("/")
def index():
    return "Bot is running!", 200

if __name__ == "__main__":
    # Render автоматты портты береді
    app.run(host="0.0.0.0", port=PORT)