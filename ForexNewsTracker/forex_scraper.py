import cloudscraper  # Use cloudscraper to bypass Cloudflare protection
import certifi       # For SSL certificate verification
from bs4 import BeautifulSoup, Tag
import logging
from config import DISCORD_WEBHOOK_URL, CHANNEL_ID, DEBUG_MODE, FOREX_FACTORY_URL, HEADERS, IMPACT_MAPPING, TODAY, TIMEZONE
import datetime
from typing import List, Dict, Any, Optional

class ForexScraper:
    def __init__(self):
        self.posted_events = set()

    async def fetch_daily_news(self) -> List[Dict[str, Any]]:
        """
        Fetch and parse the daily Forex Factory economic calendar,
        extracting only the event title, time, and impact (folder color).
        """
        try:
            logging.info("\n=== STARTING FOREX FACTORY SCRAPE ===")
            logging.info(f"Current date (EST): {TODAY}")

            # Use cloudscraper instead of requests
            scraper = cloudscraper.create_scraper()
            response = scraper.get(FOREX_FACTORY_URL, headers=HEADERS, verify=certifi.where(), timeout=10)
            response.raise_for_status()

            # Parse the HTML and locate the calendar table
            soup = BeautifulSoup(response.content, "lxml")
            calendar_table = soup.find("table", class_="calendar__table")
            if not calendar_table:
                logging.error("❌ No calendar table found!")
                logging.info("Sample of received HTML:")
                logging.info(soup.prettify()[:500])
                return []

            events = []
            # Get all rows from the table
            rows = calendar_table.find_all("tr")
            logging.info(f"\nProcessing {len(rows)} rows in the calendar table")

            current_date = None
            for row_num, tr in enumerate(rows, 1):
                try:
                    # Check for a date marker row.
                    date_cell = tr.select_one("td.calendar__cell.calendar__date.date")
                    if date_cell and date_cell.get_text(strip=True):
                        current_date = date_cell.get_text(strip=True)
                        logging.info(f"Row {row_num}: New date detected: '{current_date}'")
                    
                    # Only process rows if the current date matches our target (TODAY)
                    if current_date:
                        logging.info(f"Row {row_num}: Comparing current_date '{current_date}' with TODAY '{TODAY}'")
                        if current_date.lower() != TODAY.lower():
                            logging.info("Date does not match TODAY, skipping row")
                            continue

                    # Extract time information
                    time_cell = tr.select_one("td.calendar__cell.calendar__time.time")
                    time_text = time_cell.get_text(strip=True) if time_cell else "All Day"

                    # Extract the event title
                    event_cell = tr.select_one("td.calendar__cell.calendar__event.event")
                    if not event_cell:
                        logging.info(f"Row {row_num}: No event cell found, skipping row")
                        continue
                    event_title = event_cell.get_text(strip=True)

                    # Extract impact information (e.g., folder color such as "red")
                    impact_span = tr.select_one("td.calendar__cell.calendar__impact.impact span")
                    impact = self._get_impact(impact_span)

                    # Build event data with only the needed fields
                    event_data = {
                        "time": time_text,
                        "title": event_title,
                        "impact": impact
                    }

                    events.append(event_data)
                    logging.info(f"Row {row_num}: Event added: {event_data}")

                except Exception as e:
                    logging.error(f"Error parsing row #{row_num}: {str(e)}", exc_info=True)
                    continue

            logging.info(f"\nTotal events found for TODAY: {len(events)}")
            # Optionally sort events by time (if the time strings are comparable)
            return sorted(events, key=lambda x: x['time'])

        except Exception as e:
            logging.error(f"Error fetching forex data: {str(e)}", exc_info=True)
            return []

    def _get_impact(self, impact_cell: Optional[Tag]) -> str:
        """Extract the impact level (folder color) from the impact cell."""
        if not impact_cell or not isinstance(impact_cell, Tag):
            return "⚪ Unknown"
        impact_classes = impact_cell.get("class", [])
        # Typically, the second class contains the impact color information.
        impact_color = impact_classes[1] if len(impact_classes) > 1 else "unknown"
        return IMPACT_MAPPING.get(impact_color, "⚪ Unknown")
