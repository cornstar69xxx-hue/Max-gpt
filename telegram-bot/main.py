import os
import asyncio
import sys
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
# ✅ CORRECT pour la lib google-genai
import google.genai as genai 

# === 1. CONFIG & VÉRIFICATION DES VARIABLES D'ENVIRONNEMENT ===
print("--- DÉBUT INITIALISATION BOT ---")

# Variables cruciales pour Render
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# WEBHOOK_URL est fourni par Render pour le service Web
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL")
# Le port DOIT être lu depuis l'environnement (Render le fournit)
PORT = int(os.environ.get("PORT", 5000)) 

# Vérification rapide (ces messages apparaîtront dans les logs Render)
if not BOT_TOKEN:
    print("ERREUR: BOT_TOKEN n'est pas défini. Le bot ne peut pas fonctionner.")
    sys.exit(1)
if not GEMINI_API_KEY:
    print("AVERTISSEMENT: GEMINI_API_KEY n'est pas défini. L'IA sera désactivée.")
    # On permet au bot de démarrer, mais l'IA ne fonctionnera pas
if not WEBHOOK_URL:
    # C'est normal si vous testez en local, mais doit être défini sur Render
    print("AVERTISSEMENT: RENDER_EXTERNAL_URL n'est pas défini. Utilisation d'un URL par défaut.")
    WEBHOOK_URL = "http://localhost:5000"


# === 2. INITIALISATION GOOGLE GENAI ===
client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        print("✅ Client Gemini initialisé.")
    except Exception as e:
        print(f"ERREUR: Échec de l'initialisation du client Gemini: {e}")
        client = None

# === 3. FLASK APP ===
app = Flask(__name__)
print("✅ Application Flask créée.")

# === 4. INITIALISATION DU BOT TELEGRAM ===
application = Application.builder().token(BOT_TOKEN).build()
print("✅ Application Telegram construite.")


# === 5. FONCTION IA SYNCHRONE (Bloquante) ===
def _synchronous_generate_roast(message: str) -> str:
    """
    Fonction synchrone d'appel à l'API Gemini.
    """
    if not client:
        return "💀 RoastBot est hors service (Clé Gemini manquante ou invalide)."
        
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

        return response.text.strip()
    except Exception as e:
        # Affiche l'erreur complète dans les logs
        print(f"ERREUR API GEMINI: {e}") 
        return f"💀 Oups, j’ai buggé chef. (Erreur interne de l'IA)"


# === 6. HANDLERS ASYNCHRONES ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Répond à la commande /start."""
    print(f"Commande /start reçue de {update.effective_user.id}")
    await update.message.reply_text("🔥 Yo, ici RoastBot 9000. Envoie ton message que je te clashe 👊😎")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère tous les messages texte en exécutant la fonction IA dans un thread séparé."""
    user_message = update.message.text
    print(f"Message reçu: '{user_message}'")

    # Exécution de la fonction synchrone dans un thread (non-bloquant pour l'event loop)
    roast_reply = await asyncio.to_thread(_synchronous_generate_roast, user_message)
    
    await update.message.reply_text(roast_reply)
    print("Réponse envoyée.")


# Ajout des handlers à l'Application Telegram
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


# === 7. ROUTE WEBHOOK FLASK ===
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    """Route principale recevant les updates de Telegram."""
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.update_queue.put_nowait(update)
        # On ne log pas chaque update, car c'est trop verbeux
    return "ok"


@app.route("/", methods=["GET"])
def home():
    """Route de santé pour vérifier le statut du déploiement."""
    return f"✅ RoastBot 9000 en ligne et en écoute sur {WEBHOOK_URL}. Port: {PORT}"


# === 8. FONCTION DE SETUP ASYNCHRONE DU WEBHOOK ===
async def set_webhook_and_start_app():
    """Configure le webhook et démarre le traitement des mises à jour."""
    
    bot = Bot(token=BOT_TOKEN)
    full_webhook_url = f"{WEBHOOK_URL}/{BOT_TOKEN}"

    # 1. Suppression de tout ancien webhook
    await bot.delete_webhook()
    print("🗑️ Ancien webhook supprimé.")
    
    # 2. Définition du nouveau webhook
    await bot.set_webhook(url=full_webhook_url)
    print(f"🔗 Webhook DÉFINI sur : {full_webhook_url}")

    # 3. Démarrage de l'Application (pour gérer la file d'attente des updates)
    application.start()
    print("🔄 Application Telegram démarrée (prête à traiter les updates).")

# === 9. MAIN EXECUTION ===
if __name__ == "__main__":
    # Assurez-vous que l'exécution principale ne se fait qu'une seule fois
    print("--- DÉMARRAGE DU SERVICE ---")
    
    try:
        # Exécute la configuration asynchrone (y compris l'appel à Telegram pour le webhook)
        asyncio.run(set_webhook_and_start_app())
        
        # Le serveur Flask DOIT écouter 0.0.0.0 et le PORT fourni par Render.
        print(f"🚀 Serveur Flask prêt à servir sur 0.0.0.0:{PORT}")
        app.run(host="0.0.0.0", port=PORT)
    except Exception as e:
        print(f"FATAL: Erreur de lancement du serveur ou de l'application: {e}")
        # Arrête l'application Telegram en cas d'erreur
        application.stop()
        sys.exit(1)
