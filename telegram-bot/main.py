import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.genai as genai  # ✅ CORRECT pour la lib google-genai

# === CONFIG ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL")

# === INITIALISATION GOOGLE GENAI ===
client = genai.Client(api_key=GEMINI_API_KEY)

# === FLASK APP ===
app = Flask(__name__)

# === INITIALISATION DU BOT TELEGRAM ===
application = Application.builder().token(BOT_TOKEN).build()


# === FONCTION IA ===
def generate_roast(message: str) -> str:
    try:
        prompt = f"""
        Tu es RoastBot 9000, un bot sarcastique et drôle.
        Réponds avec humour et un peu de piquant, sans être méchant.
        Message utilisateur : {message}
        """

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )

        return response.output_text.strip()
    except Exception as e:
        return f"💀 Oups, j’ai buggé chef : {e}"


# === HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Yo, ici RoastBot 9000. Envoie ton message que je te clashe 👊😎")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    roast_reply = generate_roast(user_message)
    await update.message.reply_text(roast_reply)


# === ROUTE WEBHOOK ===
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"


@app.route("/", methods=["GET"])
def home():
    return "✅ RoastBot 9000 en ligne sur Render !"


# === MAIN ===
if __name__ == "__main__":
    import asyncio
    from telegram import Bot

    bot = Bot(token=BOT_TOKEN)
    asyncio.run(bot.delete_webhook())
    asyncio.run(bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}"))
    print(f"🔗 Webhook défini sur : {WEBHOOK_URL}/{BOT_TOKEN}")

    application.run_polling()
    app.run(host="0.0.0.0", port=10000)
