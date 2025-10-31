import os
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

# ========================
# CONFIGURATION DU LOGGING
# ========================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========================
# VARIABLES D’ENVIRONNEMENT
# ========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not TELEGRAM_TOKEN or not GOOGLE_API_KEY:
    raise ValueError("⚠️ Erreur : Les variables TELEGRAM_TOKEN et GOOGLE_API_KEY doivent être définies sur Render.")

# ========================
# INITIALISATION DU CLIENT GEMINI
# ========================
client = genai.Client(api_key=GOOGLE_API_KEY)

# ========================
# COMMANDE /start
# ========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Le bot RoastBot 9000 est en ligne ! Envoie-moi un message et je te réponds 😎")

# ========================
# RÉPONSE AUX MESSAGES
# ========================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"Roast ce message de manière drôle et sarcastique : {user_message}"
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        logger.error(f"Erreur Gemini: {e}")
        await update.message.reply_text("😅 Oups, je n'arrive pas à te roast là... Réessaie !")

# ========================
# SERVEUR WEB (pour Render)
# ========================
class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("<h1>Bot Telegram RoastBot 9000 est en ligne 🔥</h1>".encode('utf-8'))

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("", port), WebServer)
    logger.info(f"Serveur web lancé sur le port {port}")
    server.serve_forever()

# ========================
# LANCEMENT DU BOT
# ========================
async def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await app.run_polling()

# ========================
# EXÉCUTION
# ========================
if __name__ == "__main__":
    import threading
    bot_thread = threading.Thread(target=lambda: Application.builder().token(TELEGRAM_TOKEN).build().run_polling())
    bot_thread.daemon = True
    bot_thread.start()
    run_server()
