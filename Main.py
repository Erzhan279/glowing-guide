import os
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from bytez import Bytez

# === Орта айнымалылар ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BYTEZ_API_KEY = os.getenv("BYTEZ_API_KEY")
PORT = int(os.getenv("PORT", 5000))

if not TELEGRAM_TOKEN or not BYTEZ_API_KEY:
    raise RuntimeError("TELEGRAM_TOKEN немесе BYTEZ_API_KEY орнатылмаған!")

# === Flask қосымшасы (Render үшін порт ашу) ===
server = Flask(__name__)

@server.route('/')
def home():
    return "✅ Telegram бот жұмыс істеп тұр!"

# === Bytez және Telegram бөлігі ===
sdk = Bytez(BYTEZ_API_KEY)
MODEL_NAME = "openai/gpt-4o"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Сәлем! Мен AI ботпын. Хабарлама жазыңыз 🙂")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        model = sdk.model(MODEL_NAME)
        result = model.run([{"role": "user", "content": text}])
        if isinstance(result, tuple):
            output, error = result
            if error:
                reply = f"Қате: {error}"
            else:
                reply = output.get("content", str(output))
        else:
            reply = str(result)
    except Exception as e:
        reply = f"Қате шықты: {e}"

    await update.message.reply_text(reply)

def main():
    import threading
    from waitress import serve

    # Telegram polling бөлек ағынмен
    def run_telegram():
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        app.run_polling()

    threading.Thread(target=run_telegram).start()

    # Flask web сервер Render үшін
    serve(server, host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()