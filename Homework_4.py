from pprint import pprint
from lxml import html
import requests
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError



client = MongoClient('127.0.0.1', 27017)
db = client['NOVOSTI_1']
news_item = db.news
url = 'https://yandex.ru/news'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15'
    }
response = requests.get(url, headers = headers)
dom = html.fromstring(response.text)
news = dom.xpath("//div[contains(@class, 'news-app__content')]")


for i in news:
    news_data = {}
    title = i.xpath(".//h2[@class = 'mg-card__title']/a/text()")
    title = str(title).replace("\\xa0", " ")
    link = i.xpath(".//a[@class = 'mg-card__link']/@href")
    date = i.xpath(".//span[@class='mg-card-source__time']/text()")
    source = i.xpath(".//a[@class='mg-card__source-link']/text()")
    news_data['title'] = title
    news_data['link'] = link
    news_data['date'] = date
    news_data['source'] = source
    pprint(news_data)

    try:
        news_item.insert_one(news_data)
    except DuplicateKeyError:
        print("Новость уже добавлена ")

