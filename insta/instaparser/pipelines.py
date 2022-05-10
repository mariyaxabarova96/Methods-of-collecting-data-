# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import hashlib
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
from scrapy.utils.python import to_bytes


class InstaparserPipeline:
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.mongobase = client.instagram

    def process_item(self, item, spider):
        if item['type_info'] == 'followers' or item['type_info'] == 'following':
            item['_id'] = hashlib.sha1(to_bytes(item['username']+item['type_info']+item['f_username'])).hexdigest()
        elif item['type_info'] == 'post':
            item['_id'] = hashlib.sha1(to_bytes(item['post_photo'])).hexdigest()
        collection = self.mongobase[item['username']][item['type_info']]
        if collection.find_one({'_id': item['_id']}):
            print(f'Duplicated item {item["_id"]}')
        else:
            collection.insert_one(item)
        return item
