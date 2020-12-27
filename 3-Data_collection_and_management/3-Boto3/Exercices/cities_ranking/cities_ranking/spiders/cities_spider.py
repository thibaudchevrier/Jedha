import scrapy


class CitiesSpiderSpider(scrapy.Spider):
    name = 'cities_spider'

    start_urls = ['https://en.wikipedia.org/wiki/List_of_largest_cities']

    def parse(self, response):
        for city in response.xpath("//table[contains(@class, mw-datatable)]//tr[td[a[@title]]]"):
            yield {"cities": city.xpath("./td[@align='left'][1]/a/text()").get(),
                   "countries": city.xpath("./td[@align='left'][2]//a/text()").get()} 
