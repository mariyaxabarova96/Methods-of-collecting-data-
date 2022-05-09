import scrapy
from scrapy.http import HtmlResponse
from books.items import BooksItem

class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/search/История/']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@class ='pagination-next__text']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//div[contains(@class,'b-search-page')]"
                               "//a[contains(@href,'/books/') and "
                               "not(contains(@href,'#'))]/@href").getall()
        print(links)
        for link in links:
            yield response.follow(link, callback=self.book_parse)

    def book_parse(self, response: HtmlResponse):
        link = response.url
        name = response.xpath("//*[@id='product-info']/@data-name").get()
        author = response.xpath("//div[@class='authors']/a/text()").getall()
        main_price = response.xpath("//*[@id='product-info']/@data-price").get()
        sale_price = response.xpath("//*[@id='product-info']/@data-discount-price").get()
        rating = response.xpath("//div[@id='product-voting']/div[@id='product-voting-body']/div[@class='left']/div["
                                "@id='rate']/text()").get()

        yield BooksItem(name = name if name else None,
                        link = link,
                        author = author if author else None,
                        main_price = main_price if main_price else None,
                        sale_price = sale_price if sale_price else None,
                        rating = rating if rating else None)


