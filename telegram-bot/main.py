import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from google import genai

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "TON_TELEGRAM_BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "TA_CLE_GOOGLE_GENAI")

# Initialisation du client Google GenAI
genai_client = genai.Client(api_key=GOOGLE_API_KEY)

# === COMMANDES ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Salut ! Je suis en ligne ✅\nParle-moi 😎")

# === GESTION DES MESSAGES ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        # Réponse du modèle Google
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

# === LANCEMENT COMPATIBLE RENDER ===
if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except RuntimeError:
        # Si la boucle existe déjà (Render/Python 3.13), on la réutilise
        loop = asyncio.get_event_loop()
        loop.create_task(main())
        loop.run_forever()
