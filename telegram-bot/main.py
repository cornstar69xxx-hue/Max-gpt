import logging
import os
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import google.genai as genai

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "8447465027:AAH28UwcJ1WFSqizjWMYeJgXWLAK_7L2h6o"  # 🔹 Ton token Telegram
GEMINI_API_KEY = "AIzaSyAMmn433k349GDhIR0aiaObCxbxYFdr3uI"   # 🔹 Ta clé API Google AI Studio
MODEL = "models/gemini-2.5-pro"            # 🔹 Le modèle utilisé sur AI Studio

# --- Initialisation du client ---
client = genai.Client(api_key=GEMINI_API_KEY)

# --- Logs ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# --- Personnalité du bot ---
PERSONALITY_PROMPT = """
You are RoastBot 9000 — a sarcastic, rude, but funny chatbot.
Your mission: roast people, tease them, and deliver hilarious insults — but never cross into hate speech or real offense.
Your tone is confident, sharp, and self-aware, like a stand-up comedian who loves roasting the user.
Keep it short, punchy, and witty.
Respond in the same language the user uses.
"""

# --- Commande /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 RoastBot 9000 en ligne. Viens te faire griller 😈")

# --- Gestion des messages ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=f'{PERSONALITY_PROMPT}\nUser: {user_message}\nRoastBot 9000:'
        )
        roast = response.text.strip()
        await update.message.reply_text(roast)
    except Exception as e:
        await update.message.reply_text(f"💀 Erreur de RoastBot : {e}")

# --- Lancement du bot ---
def run_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ RoastBot 9000 connecté à Telegram et prêt à clasher 💥")
    app.run_polling()

# --- Petit serveur pour Render ---
def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    print(f"🌐 Fake web server running on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    run_server()



