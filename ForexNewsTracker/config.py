# config.py

# Use the webhook URL directly instead of a bot token.
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1341735209757839371/5AjOcm8f57EGZYNQMhr5wB1Uh3rXMSvUuw3P9RYWffkX-JG82SCioOhsp1ciLsTDoLx-"

# Your target channel id, if you need it elsewhere in your code.
CHANNEL_ID = "1341719312976711752"

# Other configuration settings:
DEBUG_MODE = True
FOREX_FACTORY_URL = 'https://www.forexfactory.com/calendar'
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

# Impact mapping if you're mapping classes to human-friendly names
IMPACT_MAPPING = {
    "red": "Major",
    "ora": "Medium",
    "yel": "Low",
    "gra": "Non-Economic"
}

# Today should match the date string on the calendar page, e.g. "Feb 19"
TODAY = "Feb 19"

# TIMEZONE, if you need it, for example:
TIMEZONE = "America/New_York"
