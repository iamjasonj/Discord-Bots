import logging
from typing import Any, Dict
import datetime
import pytz
from config import TIMEZONE

def setup_logging() -> None:
    """Configure logging settings for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='forex_news.log',
        filemode='w'
    )

def format_event_message(events: list[Dict[str, Any]]) -> str:
    """Format events into a Discord message."""
    message = "**📢 Today's Forex Economic Calendar**\n"
    for news in events:
        message += f"🕒 **{news['time']}** | {news['impact']} | **{news['event']}**\n"
    message += "\n🔗 [View Full Calendar](https://www.forexfactory.com/calendar.php)"
    return message

def get_current_date_str() -> str:
    """Get current date string in EST timezone."""
    return datetime.datetime.now(TIMEZONE).strftime("%a %b %d")

def is_posting_time() -> bool:
    """Check if it's time to post the daily update."""
    now = datetime.datetime.now(TIMEZONE)
    return now.hour == 7 and now.minute == 0
