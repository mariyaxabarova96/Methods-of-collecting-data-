# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient

class BooksPipeline:
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        mongodb = client['books_data']
        self.books_db = mongodb.books

    def process_item(self, item, spider):
        books_data = {}
        _id = item['url']

        if spider.name == 'labirint':
            _id = item['url']
        elif spider.name == 'book24':
            _id = item['url']

        books_data.update(item)
        books_data['_id'] = f'{spider.name}/{_id}'

        if _id:
            ans = self.books_db.insert_one(books_data)
            print('Сохранено : ' + ans.inserted_id)

        return item
