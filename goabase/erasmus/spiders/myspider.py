import scrapy
from scrapy.crawler import CrawlerProcess # one-file method
from datetime import datetime


class MySpider(scrapy.Spider):
    name = 'goabase'
    start_urls = [
        'https://www.goabase.net/party/?saAtt[geoloc]=Wien',
    ]

    custom_settings = {
        'FEEDS': {
            'Events.jsonl': {
                'format': 'json',
                'overwrite': True,  # If the file already exists, it will overwrite it
            },
        },
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_BROWSER_TYPE": "webkit",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
    }

    def parse(self, response):
        self.logger.info(f"Scraping main page: {response.url}")

        # Loop through each event container
        for party in response.css('#partylist article'):  # adjust selector to parent container
            # Title URL and Description
            title = party.css('.party-box span h3::text').get().strip()
            url = party.css('.party-box a::attr(href)').get()

            # fx-grow1 data (Location, Date, Venue)
            raw_data = party.css('.fx-grow1::text').getall()
            cleaned = [t.strip().replace("·", "") for t in raw_data if t.strip()]

            # Assume triples: Location, Date, Venue
            location, date_text, venue = (cleaned + [None] * 3)[:3]

            if not location or "Wien" not in location:
                continue

            # Optional: parse date to standard format
            print(date_text)
            parsed_date = self.parse_date(date_text)

            # Pass info to parse_desc via meta
            yield response.follow (
                url,
                callback=self.parse_desc,
                meta={
                    "Title": title,
                    "Link": url,
                    "Date": parsed_date,
                    "playwright": True
                }
            )

    def parse_desc(self, response):
        desc = response.css("#party_lineup ::text").get() \
               or response.css("#party_memo ::text").get() \
               or "Coming soon!"

        yield {
            "Title": response.meta["Title"],
            "Link": response.meta["Link"],
            "Date": response.meta["Date"],
            "Content": desc
        }

    def parse_date(self, date_str):
        #Convert something like 'Fri, 24 Oct 2025, 16:00' into '24.10.2025 16:00'.
        try:
            date_str = date_str.split(" - ")[0]
            date_str = date_str.replace("Sept", "Sep")
            dt = datetime.strptime(date_str, "%a, %d %b %Y, %H:%M")
            return dt.strftime("%d.%m.%Y")
        except Exception:
            print(f"Error parsing date: {date_str}")
            return None

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(MySpider)
    process.start()
