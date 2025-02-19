import pytz
import os
import datetime

# Bot Configuration
DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])  # Convert to int since Discord IDs are numbers

# Forex Factory Configuration
FOREX_URL = "https://www.forexfactory.com/calendar.php"
TIMEZONE = pytz.timezone("US/Eastern")

# Get today's date
TODAY = datetime.datetime.now(TIMEZONE).strftime("%a %b %d")

# Schedule Configuration
DAILY_POST_HOUR = 7
DAILY_POST_MINUTE = 0

# Debug Configuration
DEBUG_MODE = os.environ.get("DEBUG_MODE", "false").lower() == "true"

# Headers for requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9"
}

# Impact level mapping
IMPACT_MAPPING = {
    "high": "🔴 Major",
    "medium": "🟠 Medium",
    "low": "🟡 Low"
}