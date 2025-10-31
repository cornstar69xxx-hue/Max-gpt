import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import google.genai as genai

# --- Configuration API ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai_client = genai.Client(api_key=GEMINI_API_KEY)

# --- Commande /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 RoastBot 9000 en ligne ! Envoie-moi un message et je te clashe 🔥")

# --- Réponse automatique ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        response = genai_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"Réponds de façon drôle, piquante et provocante : {user_message}"
        )
        roast = response.text.strip()
    except Exception as e:
        roast = f"💀 Erreur : {e}"

    await update.message.reply_text(roast)

# --- Fonction du serveur fake (keep-alive) ---
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>Bot Telegram RoastBot 9000 est en ligne 🔥</h1>")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), KeepAliveHandler)
    print(f"🌐 Fake web server running on port {port}")
    server.serve_forever()

# --- Lancement principal ---
if __name__ == "__main__":
    # Lance le serveur web dans un thread séparé
    threading.Thread(target=run_server, daemon=True).start()

    # Lancer le bot dans le thread principal
    print("🤖 Démarrage de RoastBot 9000...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()
