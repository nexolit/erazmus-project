import scrapy
import re
from scrapy.crawler import CrawlerProcess
from datetime import datetime

class MySpider(scrapy.Spider):
    name = "goabase"
    start_urls = ["https://www.clublucia.at/"]

    custom_settings = {
        "FEEDS": {"Events.json": {"format": "json", "overwrite": True}},
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_BROWSER_TYPE": "webkit",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
        "LOG_LEVEL": "INFO",
    }

    async def start(self):
        # tell Scrapy to use Playwright for rendering
        for url in self.start_urls:
            yield scrapy.Request(url, meta={"playwright": True}, callback=self.parse)

    async def parse(self, response):
        self.logger.info(f"Scraping main page: {response.url}")

        for party_url in response.css('.wpem-event-action-url::attr(href)'):
            yield response.follow(party_url, callback=self.parse_desc)

    def parse_desc(self, response):
        print("Being followed")
        # Extract details
        title = response.css(".booking-title ::text").get()
        desc = response.css(".event-full-description p::text").getall()
        date_text = response.css(".big-event-date p ::text").get()
        parsed_date = self.parse_date(date_text) if date_text else None

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
            "Title": title,
            "Date": parsed_date.strftime("%d.%m.%Y"),
            "Description": content,
            "Link": response.url,
        }

    def parse_date(self, date_str):
        """Convert something like 'Fri, 24 Oct 2025, 16:00' into '24.10.2025'."""
        try:
            date_str = date_str.split(" - ")[0][:-5] + str(datetime.now().year)
            print(date_str)
            clean_date = re.sub(r'\b([A-Za-z]+)\b', lambda m: m.group(1)[:3],
                         re.sub(r'(\d+)(?:st|nd|rd|th)', r'\1', date_str))
            print(clean_date)
            return datetime.strptime(clean_date, "%a, %d %b, %Y")
        except Exception:
            print(f"Error parsing date: {date_str}")
            return None


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(MySpider)
    process.start()
