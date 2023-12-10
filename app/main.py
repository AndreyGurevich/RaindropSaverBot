import time
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import re
import requests
from config import TELEGRAM_BOT_TOKEN, RAINDROP_API_TOKEN, RAINDROP_API_ENDPOINT
import logging
import threading
import socketserver

# Configure the standard logging module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Hello! I am your URL parser bot. Send me a message, and I will find and save the URLs for you.")


def parse_url(update: Update, context: CallbackContext) -> None:
    message_text = update.message.text
    logger.info(f'New request: {message_text}')
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


def health_check_handler(request, client_address, server):
    request.sendall(b'HTTP/1.1 200 OK\r\n\r\nI am healthy!')


def main() -> None:
    # Start the HTTP server for health checks in a separate thread
    http_server_thread = threading.Thread(target=start_health_check_server)
    http_server_thread.start()
    # Wait for 5 seconds (adjust as needed)
    time.sleep(5)

    # Get the actual webhook URL
    updater = Updater(TELEGRAM_BOT_TOKEN)
    webhook_info = updater.bot.getWebhookInfo()
    cloud_run_url = webhook_info.url
    logger.info(f'cloud_run_url is {cloud_run_url}')

    # Update the webhook URL with port 443
    updater.bot.setWebhook(cloud_run_url + TELEGRAM_BOT_TOKEN, port=443)

    # Create and set up the Telegram bot handlers
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, parse_url))

    # Run the bot until you send a signal to stop it
    updater.idle()


def start_health_check_server():
    port = 8080
    httpd = socketserver.TCPServer(("0.0.0.0", port), health_check_handler)
    logger.info(f"Health check server listening on port {port}")
    httpd.serve_forever()


if __name__ == '__main__':
    main()
