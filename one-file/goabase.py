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
            'Goabase.json': {
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

            if (datetime.now().strftime("%m/%Y") != parsed_date.strftime("%m/%Y")
                    and datetime.now() < parsed_date):
                continue

            # Pass info to parse_desc via meta
            yield response.follow (
                url,
                callback=self.parse_desc,
                meta={
                    "Title": title,
                    "Link": url,
                    "Date": parsed_date.strftime("%d.%m.%Y"),
                    "playwright": True
                }
            )

    def parse_desc(self, response):
        desc = response.css("#party_lineup ::text").get() \
               or response.css("#party_memo ::text").get() \
               or "Coming soon!"

        s1 = [item.replace('\n', "") for item in desc]
        s2 = [item.replace('\nx', "") for item in s1]
        s3 = [item.replace('x ', "") for item in s2]
        s4 = [item.replace('\xa0', "") for item in s3]

        content = "".join(s4)

        # Cut content at around 350 characters, ending with a dot
        if len(content) > 350:
            # Find the last dot within the first 350 characters
            last_dot = content[:350].rfind('.')
            if last_dot != -1:
                content = content[:last_dot + 1]  # Include the dot
            else:
                # If no dot found, just cut at 350 characters
                content = content[:350] + "..."

        yield {
            "🌃 Title": response.meta["Title"],
            "📅 Date": response.meta["Date"],
            "🗯 Description": content,
            "🔗 Link": response.meta["Link"],
        }

    def parse_date(self, date_str):
        #Convert something like 'Fri, 24 Oct 2025, 16:00' into '24.10.2025 16:00'.
        try:
            date_str = date_str.split(" - ")[0]
            date_str = date_str.replace("Sept", "Sep")
            return datetime.strptime(date_str, "%a, %d %b %Y, %H:%M")
        except Exception:
            print(f"Error parsing date: {date_str}")
            return None

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(MySpider)
    process.start()
