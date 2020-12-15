import scrapy


class YelpSpiderSpider(scrapy.Spider):
    name = 'yelp_spider'

    start_urls = ['https://www.yelp.fr/']

    def parse(self, response):
        # FormRequest used to login
        return scrapy.FormRequest.from_response(
            response,
            formdata={'find_desc': "restaurant japonais", 'find_loc': 'Paris'},
            callback=self.after_search
        )
    
    def after_search(self, response):
        for search in response.xpath('//h4[contains(@class, heading--h4__09f24__2ijYq)]//a'):
            yield {
                'name': search.xpath('./@name').get(),
                'url': response.urljoin(search.xpath('./@href').get()),
            }
            
        # Select the NEXT button and store it in next_page
        next_page = response.xpath("//div[descendant::span[contains(@aria-current, 'true')]]/following-sibling::div//a/@href").get()

        # Check if next_page exists
        if next_page is not None:
            # Follow the next page and use the callback parse
            yield response.follow(next_page, callback=self.after_search)
        
        
