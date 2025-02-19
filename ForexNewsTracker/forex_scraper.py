import requests
from bs4 import BeautifulSoup, Tag
import logging
from config import FOREX_URL, HEADERS, IMPACT_MAPPING, TODAY, TIMEZONE
import datetime
from typing import List, Dict, Any, Optional

class ForexScraper:
    def __init__(self):
        self.posted_events = set()

    async def fetch_daily_news(self) -> List[Dict[str, Any]]:
        """Fetch and parse the daily forex economic calendar."""
        try:
            logging.info("\n=== STARTING FOREX FACTORY SCRAPE ===")
            logging.info(f"Current date (EST): {TODAY}")

            response = requests.get(FOREX_URL, headers=HEADERS, timeout=10)
            response.raise_for_status()

            # Parse HTML and get table
            soup = BeautifulSoup(response.text, "lxml")
            calendar_table = soup.find("table", class_="calendar__table")

            if not calendar_table:
                logging.error("❌ No calendar table found!")
                logging.info("Sample of received HTML:")
                logging.info(soup.prettify()[:500])
                return []

            events = []
            rows = calendar_table.select("tr.calendar__row.calendar_row")
            logging.info(f"\nProcessing {len(rows)} event rows")

            # First, let's examine all date cells
            date_cells = calendar_table.select("td.calendar__cell.calendar__date.date")
            logging.info("\nAll date cells found:")
            for i, cell in enumerate(date_cells, 1):
                date_text = cell.get_text(strip=True)
                logging.info(f"{i}. '{date_text}'")

            current_date = None
            for row_num, tr in enumerate(rows, 1):
                try:
                    logging.info(f"\n--- Processing Row #{row_num} ---")

                    # Get date cell (if present)
                    date_cell = tr.select_one("td.calendar__cell.calendar__date.date")
                    if date_cell and date_cell.get_text(strip=True):
                        current_date = date_cell.get_text(strip=True)
                        logging.info(f"Found new date marker: '{current_date}'")

                    # Compare current_date with today
                    if current_date:
                        logging.info(f"Comparing dates - Current: '{current_date}' vs Today: '{TODAY}'")
                        if current_date.lower() != TODAY.lower():
                            logging.info("Date doesn't match - skipping row")
                            continue

                    # Extract all cells
                    cells = {
                        'date': tr.select_one("td.calendar__cell.calendar__date.date"),
                        'currency': tr.select_one("td.calendar__cell.calendar__currency.currency"),
                        'impact': tr.select_one("td.calendar__cell.calendar__impact.impact span"),
                        'event': tr.select_one("td.calendar__cell.calendar__event.event"),
                        'actual': tr.select_one("td.calendar__cell.calendar__actual.actual"),
                        'forecast': tr.select_one("td.calendar__cell.calendar__forecast.forecast"),
                        'previous': tr.select_one("td.calendar__cell.calendar__previous.previous")
                    }

                    # Log found cells
                    logging.info("Cell contents:")
                    for key, cell in cells.items():
                        if cell:
                            logging.info(f"{key}: '{cell.get_text(strip=True)}'")

                    # Skip if essential cells are missing
                    if not (cells['event'] and cells['currency']):
                        logging.info("Skipping - missing essential cells")
                        continue

                    # Create event data
                    event_data = {
                        "date": cells['date'].get_text(strip=True) if cells['date'] else "All Day",
                        "currency": cells['currency'].get_text(strip=True),
                        "event": cells['event'].get_text(strip=True),
                        "impact": self._get_impact(cells['impact'])
                    }

                    # Add numerical values
                    for field in ['actual', 'forecast', 'previous']:
                        if cells[field]:
                            value = cells[field].get_text(strip=True)
                            if value:
                                event_data[field] = value

                    events.append(event_data)
                    logging.info("✅ Event added successfully")

                except Exception as e:
                    logging.error(f"Error parsing row #{row_num}: {str(e)}", exc_info=True)
                    continue

            logging.info(f"\nTotal events found: {len(events)}")
            return sorted(events, key=lambda x: x['date'] if x['date'] != 'All Day' else '00:00')

        except Exception as e:
            logging.error(f"Error fetching forex data: {str(e)}", exc_info=True)
            return []

    def _get_impact(self, impact_cell: Optional[Tag]) -> str:
        """Extract impact level from cell."""
        if not impact_cell or not isinstance(impact_cell, Tag):
            return "⚪ Unknown"

        impact_classes = impact_cell.get('class', [])
        impact_color = impact_classes[1] if len(impact_classes) > 1 else "unknown"
        return IMPACT_MAPPING.get(impact_color, "⚪ Unknown")
