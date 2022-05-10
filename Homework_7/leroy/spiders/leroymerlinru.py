import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from leroy.items import LeroyItem

class LeroymerlinruSpider(scrapy.Spider):
    name = 'leroymerlinru'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ['https://leroymerlin.ru/search/?q=дача']

    def __init__(self, name = None, **kwargs):
        super().__init__(name, **kwargs)
        self.start_urls = [f"https://leroymerlin.ru/search/?q={kwargs.get('query')}"]

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@class='bex6mjh_plp s15wh9uj_plp']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath("//product-card//a/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.parse_items)

    def parse_items(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroyItem(), response=response)
        loader.add_value('url', response.url)
        loader.add_xpath('name', "//h1/text()" )
        loader.add_xpath('photos', "//*[@slot='media-content']//picture//source[position()=1]/@data-origin")
        loader.add_xpath('price', "//*[@class='primary-price']//*[@itemprop='price']/@content")
        yield loader.load_item()






