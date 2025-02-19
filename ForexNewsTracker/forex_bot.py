import asyncio
from forex_scraper import ForexScraper
from config import DISCORD_WEBHOOK_URL, CHANNEL_ID, DEBUG_MODE

def send_to_discord(news_events):
    import cloudscraper
    import certifi
    message = "Today's ForexFactory News Events:\n" + "\n".join(
        f"{event['time']} | {event['impact']} | {event['title']}" for event in news_events
    )
    data = {'content': message}
    scraper = cloudscraper.create_scraper()
    response = scraper.post(DISCORD_WEBHOOK_URL, json=data, verify=certifi.where())
    if response.status_code == 204:
        print('Message sent successfully.')
    else:
        print('Failed to send message:', response.content)

async def main():
    scraper = ForexScraper()
    news_events = await scraper.fetch_daily_news()
    if news_events:
        send_to_discord(news_events)
    else:
        print("No news events found for today.")

if __name__ == '__main__':
    asyncio.run(main())

