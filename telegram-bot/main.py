import os
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# -----------------------------
# 🔧 Configuration des clés
# -----------------------------
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
GENAI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TELEGRAM_TOKEN or not GENAI_API_KEY:
    raise ValueError("🚨 Erreur : BOT_TOKEN ou GEMINI_API_KEY manquant dans Render !")

# -----------------------------
# 🤖 Configuration Gemini
# -----------------------------
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# -----------------------------
# 🧠 Réponse du bot
# -----------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        response = model.generate_content(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("😢 Erreur interne du bot.")
        print("Erreur Gemini :", e)

# -----------------------------
# 🚀 Flask (pour Render)
# -----------------------------
app_flask = Flask(__name__)

@app_flask.route("/")
def home():
    return "🤖 Bot Telegram en ligne et fonctionnel !"

# -----------------------------
# ▶️ Lancement du bot
# -----------------------------
def start_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Bot Telegram démarré avec succès !")
    app.run_polling()

if __name__ == "__main__":
    start_bot()
