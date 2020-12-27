import scrapy


class WikiSpiderSpider(scrapy.Spider):
    name = 'wiki_spider'
    
    start_urls = ['https://en.wikipedia.org/wiki/Machine_learning']

    def parse(self, response):
        for paragraph in response.xpath("//div[@class='mw-parser-output']/p"):
            yield {"paragraph": paragraph.xpath(".//text()").extract()}
