import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.genai as genai

# === CONFIGURATION ===
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_URL")

# Vérification
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN manquant dans les variables d'environnement.")
if not GOOGLE_API_KEY:
    raise ValueError("❌ GOOGLE_API_KEY manquant dans les variables d'environnement.")

# === INITIALISATION ===
app = Flask(__name__)

# Configuration Google AI
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# === HANDLERS TELEGRAM ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Salut ! Je suis ton bot connecté à Google AI Studio !")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        response = model.generate_content(user_text)
        await update.message.reply_text(response.text or "🤖 Je n’ai pas pu générer de réponse.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Erreur : {str(e)}")

# === APPLICATION TELEGRAM ===
application = Application.builder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

# === FLASK SERVER POUR RENDER ===
@app.route("/", methods=["GET"])
def home():
    return "✅ Bot en ligne sur Render !"

@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        application.update_queue.put(update)
        return "ok", 200

# === LANCEMENT LOCAL / RENDER ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Serveur Flask en ligne sur le port {port}")

    # Si URL Render disponible → configure webhook
    if WEBHOOK_URL:
        from telegram import Bot
        bot = Bot(token=BOT_TOKEN)
        bot.delete_webhook()
        bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
        print(f"🔗 Webhook défini sur : {WEBHOOK_URL}/webhook")

    app.run(host="0.0.0.0", port=port)
