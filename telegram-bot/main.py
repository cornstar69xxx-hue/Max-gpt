import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# === CONFIG ===
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL")

# ✅ Nouvelle méthode correcte pour initialiser Google AI
genai.configure(api_key=GOOGLE_API_KEY)

# === FLASK APP ===
app = Flask(__name__)

# === INITIALISATION DU BOT ===
application = Application.builder().token(BOT_TOKEN).build()

# === FONCTION IA ===
def generate_roast(message: str) -> str:
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = (
            f"Tu es RoastBot 9000, un bot sarcastique et drôle. "
            f"Réponds avec humour et un peu de piquant, sans être méchant. "
            f"Message utilisateur : {message}"
        )
        response = model.generate_content(prompt)
        return response.text or "😏 Même moi je sais pas quoi te dire, c’est chaud..."
    except Exception as e:
        return f"💀 Oups, j’ai bugé chef : {e}"

# === HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Yo, ici RoastBot 9000. Balance ton message que je te clashe 💬🔥")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    print(f"[MESSAGE] {user_message}")
    roast_response = generate_roast(user_message)
    await update.message.reply_text(roast_response)

# === AJOUT DES HANDLERS ===
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# === ROUTES FLASK ===
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok", 200

@app.route("/")
def home():
    return "🔥 RoastBot 9000 est en ligne et prêt à clasher !"

# === LANCEMENT SERVEUR + WEBHOOK ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Serveur Flask en ligne sur le port {port}")

    if WEBHOOK_URL:
        bot = Bot(token=BOT_TOKEN)
        bot.delete_webhook()
        bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
        print(f"🔗 Webhook défini sur : {WEBHOOK_URL}/webhook")

    app.run(host="0.0.0.0", port=port)
