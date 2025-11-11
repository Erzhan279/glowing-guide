# Main.py
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from bytez import Bytez  # Bytez SDK

# --- Орта айнымалылардан токендер ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BYTEZ_API_KEY = os.getenv("BYTEZ_API_KEY")

if not TELEGRAM_TOKEN or not BYTEZ_API_KEY:
    raise RuntimeError("TELEGRAM_TOKEN немесе BYTEZ_API_KEY орнатылмаған!")

# --- Bytez SDK бастау ---
sdk = Bytez(BYTEZ_API_KEY)
MODEL_NAME = "openai/gpt-4o"

# --- /start командасы ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Сәлем! Мен AI ботпын. Мәтінді жазыңыз, мен жауап беремін."
    )

# --- Пайдаланушы хабарламасын өңдеу ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    model = sdk.model(MODEL_NAME)

    try:
        output, error = model.run([{"role": "user", "content": user_text}])

        if error:
            reply = f"Қате шықты: {error}"
        else:
            # Bytez кейде dict, кейде str қайтарады
            if isinstance(output, dict) and "content" in output:
                reply = output["content"]
            elif isinstance(output, str):
                reply = output
            else:
                reply = str(output)

    except Exception as e:
        reply = f"Қате шықты: {e}"

    await update.message.reply_text(reply)

# --- Ботты іске қосу ---
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот іске қосылды...")
    app.run_polling()

if __name__ == "__main__":
    main()