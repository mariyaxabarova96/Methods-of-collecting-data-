# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BooksItem(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field()
    authors = scrapy.Field()
    link = scrapy.Field()
    main_price = scrapy.Field()
    sale_price = scrapy.Field()
    rating = scrapy.Field()
    pass
