import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from google import genai
import asyncio

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "TON_TELEGRAM_BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "TA_CLE_GOOGLE_GENAI")

# Initialisation du client Google GenAI
genai_client = genai.Client(api_key=GOOGLE_API_KEY)

# === COMMANDES ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Salut ! Je suis en ligne ✅\nParle-moi 😎")

# === RÉPONSES AUTOMATIQUES ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        # Appel à Google GenAI (Gemini)
        response = genai_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=user_message
        )
        bot_reply = response.text.strip()
    except Exception as e:
        bot_reply = f"❌ Erreur : {e}"

    await update.message.reply_text(bot_reply)

# === MAIN ===
async def main():
    print("🚀 Lancement du bot Telegram...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Ajout des handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot en mode polling — prêt à discuter !")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
