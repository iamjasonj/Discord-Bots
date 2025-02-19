import asyncio
import datetime
import pytz
import logging
from forex_scraper import ForexScraper
from config import DISCORD_WEBHOOK_URL, CHANNEL_ID, DEBUG_MODE, TODAY, TIMEZONE

import cloudscraper
import certifi

def send_to_discord(news_events):
    """Format the news events and send them via Discord webhook."""
    message_lines = ["**📢 Today's Forex Economic Calendar**"]
    for event in news_events:
        message_lines.append(f"🕒 **{event['time']}** | {event['impact']} | **{event['title']}**")
    message_lines.append("\n🔗 [View Full Calendar](https://www.forexfactory.com/calendar)")
    message = "\n".join(message_lines)
    
    scraper = cloudscraper.create_scraper()
    data = {"content": message}
    response = scraper.post(DISCORD_WEBHOOK_URL, json=data, verify=certifi.where())
    if response.status_code == 204:
        logging.info('Message sent successfully.')
    else:
        logging.error('Failed to send message: ' + str(response.content))

async def run_bot():
    scraper = ForexScraper()
    while True:
        now = datetime.datetime.now(pytz.timezone(TIMEZONE))
        logging.info(f"Current time: {now.strftime('%I:%M %p')}")
        # Check if the time is exactly 7:00 AM EST.
        if now.hour == 7 and now.minute == 0:
            logging.info("It's 7:00 AM EST. Fetching news events...")
            news_events = await scraper.fetch_daily_news()
            if news_events:
                send_to_discord(news_events)
            else:
                logging.info("No news events found for today.")
            # Sleep a little over one minute to avoid duplicate posting
            await asyncio.sleep(61)
        else:
            await asyncio.sleep(30)

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='forex_news.log',
        filemode='a'
    )
    asyncio.run(run_bot())

if __name__ == '__main__':
    main()
