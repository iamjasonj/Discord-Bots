import discord
import asyncio
import logging
from config import DISCORD_TOKEN, CHANNEL_ID, DEBUG_MODE
from forex_scraper import ForexScraper
from utils import setup_logging, is_posting_time

class ForexBot:
    def __init__(self):
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.intents.guild_messages = True
        self.client = discord.Client(intents=self.intents)
        self.scraper = ForexScraper()
        setup_logging()

        @self.client.event
        async def on_ready():
            print(f"✅ Bot is online as {self.client.user}")
            self.client.loop.create_task(self._post_daily_news())

        @self.client.event
        async def on_message(message):
            if message.author == self.client.user:
                return

            if DEBUG_MODE and message.content.startswith('!test_forex'):
                await self._fetch_and_post_news(message.channel)

    async def _format_event_message(self, events):
        """Format events into a Discord message with detailed information."""
        if not events:
            return "No forex events found for today."

        message = "**📢 Today's Forex Economic Calendar**\n\n"
        for event in events:
            # Format the event details
            impact = event['impact']
            time = event['time']
            currency = event['currency']
            title = event['event']

            # Add the main event information
            message += f"**{time}** | {currency} | {impact} | **{title}**\n"

            # Add the numerical values if they exist
            values = []
            if 'actual' in event:
                values.append(f"Actual: {event['actual']}")
            if 'forecast' in event:
                values.append(f"Forecast: {event['forecast']}")
            if 'previous' in event:
                values.append(f"Previous: {event['previous']}")

            if values:
                message += f"├─ {' | '.join(values)}\n"
            message += "\n"

        message += "🔗 [View Full Calendar](https://www.forexfactory.com/calendar.php)"
        return message

    async def _check_channel_permissions(self, channel):
        if not channel:
            logging.error("❌ Channel not found!")
            return False

        permissions = channel.permissions_for(channel.guild.me)
        if not permissions.send_messages:
            logging.error(f"❌ Bot lacks permission to send messages in channel: {channel.name}")
            return False
        return True

    async def _fetch_and_post_news(self, channel):
        if not await self._check_channel_permissions(channel):
            return

        try:
            news_events = await self.scraper.fetch_daily_news()
            message = await self._format_event_message(news_events)
            await channel.send(message)

            if news_events:
                logging.info(f"✅ Posted {len(news_events)} forex events to Discord")
            else:
                logging.warning("⚠️ No forex events were found")

        except discord.Forbidden:
            logging.error(f"❌ Bot lacks permission to send messages in channel: {channel.name}")
        except Exception as e:
            error_msg = f"❌ Error fetching/posting forex news: {str(e)}"
            logging.error(error_msg)
            if DEBUG_MODE:
                await channel.send(error_msg)

    async def _post_daily_news(self):
        await self.client.wait_until_ready()
        channel = self.client.get_channel(CHANNEL_ID)

        while not self.client.is_closed():
            if is_posting_time():
                if await self._check_channel_permissions(channel):
                    await self._fetch_and_post_news(channel)
                await asyncio.sleep(86400)  # Wait 24 hours
            else:
                await asyncio.sleep(60)  # Check again in 60 seconds

    def run(self):
        self.client.run(DISCORD_TOKEN)

if __name__ == "__main__":
    bot = ForexBot()
    bot.run()