import scrapy
from scrapy.http import HtmlResponse
from books.items import BooksItem

class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']
    page = 1
    start_urls = ['https://book24.ru/search/page-{page}/?q=история']

    def parse(self, response:HtmlResponse):
        for i in range(524):
            pages = self.start_urls.replace('{page}', str(i))
            yield response.follow(pages, callback=self.parse)

        links = response.xpath("//*[@class='product-list__item']//a[contains(@href, '/product/')]/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.book_parse)

    def book_parse(self, response:HtmlResponse):
        link = response.url
        name = response.xpath("//div[@class='product-detail-page__title-holder']/h1/text()").get()
        author = response.xpath("//*[@itemprop='author']//*[@itemprop='name']/@content").getall()
        main_price =  response.xpath("//*[@itemprop='price']/@content").get()
        sale_price =  response.xpath("//*[@class='product-sidebar-price__price-old']//text()").get()
        rating = response.xpath("//*[@itemprop='ratingValue']/@content").get()

        yield BooksItem(name = name if name else None,
                        link = link,
                        author = author if author else None,
                        main_price = main_price if main_price else None,
                        sale_price = sale_price if sale_price else None,
                        rating = rating if rating else None)


