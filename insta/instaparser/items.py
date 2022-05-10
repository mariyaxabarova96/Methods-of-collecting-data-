# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    user_id = scrapy.Field()
    username = scrapy.Field()
    photo = scrapy.Field()
    likes = scrapy.Field()
    post_data = scrapy.Field()
    _id = scrapy.Field()
    type_info = scrapy.Field()
    fol_u_id = scrapy.Field()
    fol_u_name = scrapy.Field()
    url = scrapy.Field()
    profile_photo = scrapy.Field()