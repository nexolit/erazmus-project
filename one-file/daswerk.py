import re
import scrapy
from scrapy.crawler import CrawlerProcess
from datetime import datetime


class MySpider(scrapy.Spider):
    name = 'daswerk'
    start_urls = [
        'https://www.daswerk.org/programm',
    ]

    custom_settings = {
        "FEEDS": { "Events.jsonl": {
            "format": "jsonlines",
            "store_empty": False,
            "overwrite": False,  # <- key to add new items instead of overwriting
        }},
    }

    def parse(self, response):
        # Route by domain to discover event links
        url = response.url
        self.logger.info(f"Scraping main page: {url}")

        links = response.css('a.preview-item--link::attr(href)').getall()

        for link in links:
            yield response.follow(link, callback=self.parse_event)

    def parse_event(self, response):
        url = response.url

        # Collect content text from main areas
        content = response.css('.detail-content ::text').getall()

        s1 = [item.replace('\n', " ") for item in content]
        s2 = [item.replace('\nx', "") for item in s1]
        s3 = [item.replace('x ', "") for item in s2]
        s4 = [item.replace('\xa0', "") for item in s3]

        content = " ".join(s4)

        # Cut content at around 350 characters, ending with a dot
        if len(content) > 350:
            # Find the last dot within the first 350 characters
            last_dot = content[:350].rfind('.')
            if last_dot != -1:
                content = content[:last_dot + 1]  # Include the dot
            else:
                # If no dot found, just cut at 350 characters
                content = content[:350] + "..."

        title = response.css('p.main--header-title::text').get()

        date = self.clean_date(response.css('li:nth-child(1)::text').get())
        time = response.css('li:nth-child(2)::text').get()

        today_date = datetime.strftime(datetime.today(), "%#d. %#m. %Y")
        if date != today_date:
            yield None

        yield {
            'Title': title.strip(),
            'Date': date.strip(),
            'Description': content,
            'Time': time.strip(),
            'Link': url,
        }

    def clean_date(self, date):
        # Mapping German month names to numbers
        months = {
            "Januar": 1,
            "Februar": 2,
            "März": 3,
            "April": 4,
            "Mai": 5,
            "Juni": 6,
            "Juli": 7,
            "August": 8,
            "September": 9,
            "Oktober": 10,
            "November": 11,
            "Dezember": 12
        }

        # Regex to extract day, month, optional year
        match = re.search(r"\b(\d{1,2})\.?\s+(\w+)(?:\s+(\d{4}))?", date)

        if match:
            day = int(match.group(1))
            month_name = match.group(2)
            month_num = months[month_name]
            year = int(match.group(3)) if match.group(3) else datetime.now().year
            result = f"{day}.{month_num}.{year}"
            return result  # Example Output: 9.11.[YEAR] or 9.11.2025 if no year in input
        return None

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(MySpider)
    process.start()
