import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import google.genai as genai

# --- Configuration ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

# --- Vérification des clés ---
if not TELEGRAM_TOKEN or not GENAI_API_KEY:
    raise ValueError("🚨 TELEGRAM_TOKEN ou GENAI_API_KEY manquant dans les variables Render !")

# --- Client Gemini ---
genai_client = genai.Client(api_key=GENAI_API_KEY)

# --- Flask pour Render keep-alive ---
web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "✅ RoastBot 9000 est en ligne sur Render !"

# --- Handler Telegram ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logger.info(f"Message reçu : {user_message}")

    try:
        response = genai_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"Roast this user humorously: {user_message}",
        )
        reply = response.text or "😶 Pas de réponse de l’IA."
    except Exception as e:
        logger.error(f"Erreur Gemini : {e}")
        reply = "⚠️ Erreur côté IA."

    await update.message.reply_text(reply)

# --- Fonction de lancement du bot ---
def run_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("🤖 Bot prêt. Mode polling activé.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

# --- Entrée principale ---
def main():
    # Lancer le bot dans un thread séparé
    threading.Thread(target=run_bot, daemon=True).start()

    # Lancer Flask pour garder le conteneur actif
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"🌐 Serveur Flask actif sur le port {port}")
    web_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
