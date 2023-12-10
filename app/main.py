from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import re
import requests
from os import getenv

# Define your bot token and Raindrop.io API token here
TELEGRAM_BOT_TOKEN = getenv("TELEGRAM_BOT_TOKEN")
RAINDROP_API_TOKEN = getenv("RAINDROP_API_TOKEN")


# Raindrop.io API endpoint
RAINDROP_API_ENDPOINT = "https://api.raindrop.io/rest/v1/raindrop"


# Function to handle the /start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Hello! I am your URL parser bot. Send me a message, and I will find and save the URLs for you.")


# Function to handle incoming messages
def parse_url(update: Update, context: CallbackContext) -> None:
    # Get the text of the received message
    message_text = update.message.text

    # Use regular expression to find URLs in the message
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message_text)

    if urls:
        # Save each URL to Raindrop.io
        for url in urls:
            save_url_to_raindrop(url)

        # Send a confirmation message
        update.message.reply_text(f"Found and saved the following URLs to your Raindrop.io account:\n{', '.join(urls)}")
    else:
        update.message.reply_text("No URLs found in the message.")


# Function to save a URL to Raindrop.io
def save_url_to_raindrop(url: str) -> None:
    headers = {
        "Authorization": f"Bearer {RAINDROP_API_TOKEN}",
        "Content-Type": "application/json",
    }

    data = {
        "link": url,
        "collection": 0,  # Change this to the collection ID where you want to save the links
    }

    response = requests.post(RAINDROP_API_ENDPOINT, headers=headers, json=data)

    if response.status_code == 200:
        print(f"URL '{url}' saved successfully to Raindrop.io.")
    else:
        print(f"Failed to save URL '{url}' to Raindrop.io. Status code: {response.status_code}, Response: {response.json()}")


# Main function to run the bot
def main() -> None:
    updater = Updater(TELEGRAM_BOT_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register command handlers
    dp.add_handler(CommandHandler("start", start))

    # Register a message handler to parse URLs
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, parse_url))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you send a signal to stop it
    updater.idle()


if __name__ == '__main__':
    main()
