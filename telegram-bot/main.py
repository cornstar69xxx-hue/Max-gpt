import logging
import os
import asyncio
from http.server import SimpleHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import google.genai as genai

# --- CONFIGURATION ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not BOT_TOKEN or not GEMINI_API_KEY:
    print("❌ Erreur : variables d’environnement manquantes.")
    print("BOT_TOKEN:", BOT_TOKEN)
    print("GEMINI_API_KEY:", GEMINI_API_KEY)
    raise ValueError("Les variables BOT_TOKEN et GEMINI_API_KEY doivent être définies dans Render.")

MODEL = "models/gemini-2.5-pro"
client = genai.Client(api_key=GEMINI_API_KEY)

# --- LOGGING ---
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
            contents=f"{PERSONALITY_PROMPT}\nUser: {user_message}\nRoastBot 9000:"
        )
        roast = response.text.strip()
        await update.message.reply_text(roast)
    except Exception as e:
        await update.message.reply_text(f"💀 Erreur de RoastBot : {e}")

# --- Serveur Render ---
def start_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    print(f"🌐 Fake web server running on port {port}")
    server.serve_forever()

# --- Lancement global ---
async def main():
    # Démarre le serveur HTTP dans un thread de fond
    asyncio.create_task(asyncio.to_thread(start_server))

    # Configure et démarre le bot Telegram
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ RoastBot 9000 connecté à Telegram et prêt à clasher 💥")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
