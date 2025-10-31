import os
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# --- CONFIG ---
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL")

# --- INITIALISATION GEMINI ---
genai.configure(api_key=GOOGLE_API_KEY)

# --- FLASK SERVER ---
app = Flask(__name__)

# --- TELEGRAM BOT ---
application = Application.builder().token(BOT_TOKEN).build()

# --- IA FUNCTION ---
def generate_roast(message: str) -> str:
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = (
            f"Tu es RoastBot 9000, un bot sarcastique et drôle. "
            f"Réponds avec humour et un peu de piquant, sans être méchant.\n"
            f"Message utilisateur : {message}"
        )
        response = model.generate_content(prompt)
        return response.text or "😶 Même moi je sais pas quoi te dire là..."
    except Exception as e:
        return f"💀 Oups, j’ai buggé chef : {e}"

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Yo ! Je suis RoastBot 9000. Envoie ton message, que je te clashe 😈")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    roast = generate_roast(user_message)
    await update.message.reply_text(roast)

# --- ADD HANDLERS ---
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- FLASK ROUTES ---
@app.route("/")
def home():
    return "✅ RoastBot 9000 est en ligne sur Render !"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put(update)
    return "ok"

# --- MAIN ---
if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)

    async def run():
        await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
        print(f"🔗 Webhook connecté sur : {WEBHOOK_URL}/{BOT_TOKEN}")
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

    asyncio.run(run())
