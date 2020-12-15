import scrapy


class QuotesSpider(scrapy.Spider):

    # Name of your spider
    name = "quotes"

    # Url to start your spider from 
    start_urls = [
        'http://quotes.toscrape.com/page/1/',
    ]

    # Callback that gets text, author and tags of the webpage
    def parse(self, response):
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('span small::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall(),
            }

        # Select the NEXT button and store it in next_page
        next_page = response.css('li.next a').attrib["href"]

        # Check if next_page exists
        if next_page is not None:
            # Follow the next page and use the callback parse
            yield response.follow(next_page, callback=self.parse)