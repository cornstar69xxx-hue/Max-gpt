import os
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
# Utilisation de la bonne librairie : 'google-generativeai'
from google import generativeai as genai 

# === CONFIG & VÉRIFICATION ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL")
PORT = int(os.environ.get("PORT", 5000)) # Utilisation du PORT fourni par Render

# Sortie de débogage pour les logs Render
print(f"DEBUG: BOT_TOKEN {'DÉFINI' if BOT_TOKEN else 'MANQUANT'}")
print(f"DEBUG: GEMINI_API_KEY {'DÉFINIE' if GEMINI_API_KEY else 'MANQUANTE'}")
print(f"DEBUG: WEBHOOK_URL: {WEBHOOK_URL}")

# Vérification obligatoire des clés
if not BOT_TOKEN:
    print("ERREUR: BOT_TOKEN n'est pas défini. Le bot ne peut pas fonctionner.")
    exit(1)

# === INITIALISATION GOOGLE GENAI ===
try:
    # Initialisation du client avec la nouvelle librairie
    client = genai.Client(api_key=GEMINI_API_KEY)
    print("DEBUG: Client Gemini initialisé avec succès.")
except Exception as e:
    # Note: L'absence de GEMINI_API_KEY est gérée plus tard, mais toute autre erreur est critique ici.
    print(f"ERREUR: Échec de l'initialisation du client Gemini: {e}")
    client = None

# === FLASK APP ===
app = Flask(__name__)

# === INITIALISATION DU BOT TELEGRAM ===
application = Application.builder().token(BOT_TOKEN).build()


# === FONCTION IA (Exécutée dans un thread pour l'asynchrone) ===
def generate_roast_sync(message: str) -> str:
    # Cette fonction est maintenant synchrone et est appelée via asyncio.to_thread
    if not client:
        return "⚠️ Je suis hors service. Ma clé Gemini est manquante ou invalide. 💀"
    
    try:
        prompt = f"""
        Tu es RoastBot 9000, un bot sarcastique et drôle.
        Réponds avec humour et un peu de piquant, sans être méchant.
        Ton message doit être court et percutant.
        Message utilisateur : {message}
        """

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )

        # La librairie 'google-generativeai' utilise 'text' pour le résultat
        return response.text.strip()
    except Exception as e:
        return f"💀 Oups, j’ai buggé chef (Erreur AI) : {e}"


# === HANDLERS ASYNCHRONES ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Yo, ici RoastBot 9000. Envoie ton message que je te clashe 👊😎")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    # Exécute l'appel Gemini (synchrone) dans un thread séparé pour ne pas bloquer le webhook
    roast_reply = await asyncio.to_thread(generate_roast_sync, user_message)
    await update.message.reply_text(roast_reply)


# === ROUTE WEBHOOK ===
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    # Dispatcher asynchrone pour gérer les updates du webhook
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        # On utilise process_update pour une gestion asynchrone des handlers
        await application.process_update(update)
    except Exception as e:
        print(f"ERREUR lors du traitement du webhook: {e}")
        # Retourne 200 OK même en cas d'erreur pour éviter les tentatives de renvoi par Telegram
    return "ok"


@app.route("/", methods=["GET"])
def home():
    if not WEBHOOK_URL or not BOT_TOKEN:
        return "❌ RoastBot 9000 : Erreur de configuration. Vérifiez BOT_TOKEN et RENDER_EXTERNAL_URL."
    
    status = (
        "✅ RoastBot 9000 en ligne et en écoute sur Render !"
        f"<br>🔗 Webhook configuré sur : <code>{WEBHOOK_URL}/{BOT_TOKEN}</code>"
        f"<br>🤖 Statut AI: {'✅ Prêt' if client else '❌ Invalide'}"
    )
    return status


# === FONCTION DE DÉMARRAGE ET DE CONFIGURATION DU WEBHOOK ===
async def set_webhook_and_start_app():
    # Définition du webhook au démarrage du serveur
    bot = Bot(token=BOT_TOKEN)
    
    webhook_url_full = f"{WEBHOOK_URL}/{BOT_TOKEN}"

    # Tente de définir le webhook
    try:
        current_webhook = await bot.get_webhook_info()
        if current_webhook.url != webhook_url_full:
            await bot.set_webhook(url=webhook_url_full)
            print(f"🔗 Webhook DÉFINI sur : {webhook_url_full}")
        else:
            print(f"🔗 Webhook est DÉJÀ configuré correctement : {webhook_url_full}")
    except Exception as e:
        print(f"ERREUR FATALE: Échec de la configuration du webhook: {e}")
        # Ne pas quitter si le webhook échoue, le serveur doit quand même démarrer
    
    # Ajout des handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Lance les processus de mise à jour asynchrones (nécessaire même en mode webhook)
    await application.initialize()
    await application.start()
    
    # Renvoie l'objet Flask app pour que Gunicorn puisse le lancer
    return app


# === MAIN ENTRY POINT ===
if __name__ == '__main__':
    # Cette section est ignorée par Gunicorn/Render et sert uniquement au test local.
    if not BOT_TOKEN or not WEBHOOK_URL:
        print("Veuillez définir BOT_TOKEN et RENDER_EXTERNAL_URL (ou l'utiliser via Gunicorn sur Render).")
    else:
        # Configuration du webhook et démarrage de l'application Flask
        asyncio.run(set_webhook_and_start_app())
        # Dans un environnement de production (Render), ceci est remplacé par Gunicorn
        app.run(host="0.0.0.0", port=PORT)
