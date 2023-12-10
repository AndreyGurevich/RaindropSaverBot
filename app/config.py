from os import getenv

TELEGRAM_BOT_TOKEN = getenv("TELEGRAM_BOT_TOKEN")
RAINDROP_API_TOKEN = getenv("RAINDROP_API_TOKEN")
RAINDROP_API_ENDPOINT = "https://api.raindrop.io/rest/v1/raindrop"
BOT_ENDPOINT = getenv("BOT_ENDPOINT") # Must be in format "https://your-cloud-run-service-url/"
# IDS_ALLOWED=[]