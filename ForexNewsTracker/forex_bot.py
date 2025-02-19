from config import DISCORD_WEBHOOK_URL, CHANNEL_ID, DEBUG_MODE, FOREX_FACTORY_URL, HEADERS, IMPACT_MAPPING, TODAY, TIMEZONE
import asyncio
from forex_scraper import ForexScraper

class ForexBot:
    def __init__(self):
        self.scraper = ForexScraper()
        # self.client = discord.Client()  <-- Remove this if you're not running a bot

    async def run(self):
        news_events = await self.scraper.fetch_daily_news()
        if news_events:
            send_to_discord(news_events)  # call your webhook function
        else:
            print("No news events found for today.")

def send_to_discord(news_events):
    import cloudscraper
    import certifi
    message = "Today's ForexFactory News Events:\n" + "\n".join(
        f"{event['time']} | {event['impact']} | {event['title']}" for event in news_events)
    data = {'content': message}
    scraper = cloudscraper.create_scraper()
    response = scraper.post(DISCORD_WEBHOOK_URL, json=data, verify=certifi.where())
    if response.status_code == 204:
        print('Message sent successfully.')
    else:
        print('Failed to send message:', response.content)

def main():
    bot = ForexBot()
    asyncio.run(bot.run())

if __name__ == '__main__':
    main()

