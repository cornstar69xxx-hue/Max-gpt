import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from google import genai
from google.genai import types
from flask import Flask

# --- Configuration logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Clés d'API ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

# --- Google Generative AI client ---
genai_client = genai.Client(api_key=GENAI_API_KEY)

# --- Flask app pour Render keep-alive ---
app_web = Flask(__name__)

@app_web.route("/")
def home():
    return "✅ Bot Telegram fonctionne sur Render !"

# --- Handler pour les messages Telegram ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logger.info(f"Message reçu : {user_message}")

    try:
        response = genai_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=user_message,
        )
        reply_text = response.text or "🤖 Aucune réponse générée."
    except Exception as e:
        logger.error(f"Erreur GenAI : {e}")
        reply_text = "⚠️ Erreur avec l’IA, réessaie plus tard."

    await update.message.reply_text(reply_text)

# --- Fonction principale ---
def main():
    logger.info("🚀 Lancement du bot Telegram...")

    # Lancement du bot Telegram
    app = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .build()
    )

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Lancement du serveur Flask sur Render (port défini par Render)
    port = int(os.environ.get("PORT", 8080))

    # On démarre le bot et Flask dans des threads séparés
    import threading

    threading.Thread(target=lambda: app.run_polling(allowed_updates=Update.ALL_TYPES), daemon=True).start()

    logger.info("🤖 Bot en mode polling — prêt à discuter !")

    # Flask bloque le thread principal (keep-alive Render)
    app_web.run(host="0.0.0.0", port=port)

# --- Exécution ---
if __name__ == "__main__":
    main()
