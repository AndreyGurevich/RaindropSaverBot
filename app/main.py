from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import re
import requests
from config import RAINDROP_API_ENDPOINT, BOT_ENDPOINT, RAINDROP_API_TOKEN, TELEGRAM_BOT_TOKEN

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Hello! I am your URL parser bot. Send me a message, and I will find and save the URLs for you.")

def parse_url(update: Update, context: CallbackContext) -> None:
    message_text = update.message.text
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message_text)

    if urls:
        for url in urls:
            save_url_to_raindrop(url)

        update.message.reply_text(f"Found and saved the following URLs to your Raindrop.io account:\n{', '.join(urls)}")
    else:
        update.message.reply_text("No URLs found in the message.")

def save_url_to_raindrop(url: str) -> None:
    headers = {
        "Authorization": f"Bearer {RAINDROP_API_TOKEN}",
        "Content-Type": "application/json",
    }

    data = {
        "link": url,
        "collection": 0,
    }

    response = requests.post(RAINDROP_API_ENDPOINT, headers=headers, json=data)

    if response.status_code == 200:
        print(f"URL '{url}' saved successfully to Raindrop.io.")
    else:
        print(f"Failed to save URL '{url}' to Raindrop.io. Status code: {response.status_code}, Response: {response.json()}")

def health_check(update, context):
    update.message.reply_text("I'm healthy!")

def main() -> None:
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, parse_url))
    dp.add_handler(CommandHandler("health", health_check))

    # Start the Bot with webhook
    updater.start_webhook(port=8080, listen="0.0.0.0", url_path=TELEGRAM_BOT_TOKEN)
    updater.bot.set_webhook(BOT_ENDPOINT + TELEGRAM_BOT_TOKEN)

    # Run the bot until you send a signal to stop it
    updater.idle()

if __name__ == '__main__':
    main()
