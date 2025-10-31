import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai  # ✅ Nouveau import correct

# Configuration des clés
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

app = Flask(__name__)

# ✅ Initialiser le client Google GenAI
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Fonction de démarrage du bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salut ! Je suis ton bot IA 🤖. Envoie-moi un message !")

# Fonction pour gérer les messages texte
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        response = model.generate_content(user_message)
        bot_reply = response.text or "Désolé, je n'ai pas compris 😅"
        await update.message.reply_text(bot_reply)
    except Exception as e:
        await update.message.reply_text(f"Erreur IA : {str(e)}")

# Fonction webhook (Render appelle cette URL)
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"

# Route d’accueil
@app.route("/", methods=["GET"])
def home():
    return "✅ Bot en ligne sur Render !"

# Configuration du bot Telegram
application = Application.builder().token(TELEGRAM_TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Lancer le serveur Flask (Render appelle automatiquement sur le port)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
