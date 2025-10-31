import logging
import os
from http.server import SimpleHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import google.genai as genai
import asyncio

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "models/gemini-2.0-pro"

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    print("❌ ERREUR: Variables d'environnement manquantes (BOT_TOKEN ou GEMINI_API_KEY)")
    exit(1)

print(f"✅ BOT_TOKEN chargé: {TELEGRAM_TOKEN[:10]}...")
print(f"✅ GEMINI_API_KEY chargé: {GEMINI_API_KEY[:6]}...")

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

# --- Lancement global (bot + mini serveur pour Render) ---
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Mini serveur pour Render
    async def run_server():
        port = int(os.environ.get("PORT", 10000))
        server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
        print(f"🌐 Fake web server running on port {port}")
        server.serve_forever()

    # Lance bot + serveur en parallèle
    loop = asyncio.get_event_loop()
    loop.create_task(run_server())
    print("✅ RoastBot 9000 connecté à Telegram et prêt à clasher 💥")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
