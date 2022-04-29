from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from pymongo import MongoClient
client = MongoClient('127.0.0.1', 27017)
db = client['mails']
letters_from_email = db.letters
s = Service('./chromedriver')
driver = webdriver.Chrome(service=s)

driver.get('https://account.mail.ru/login/')
elem = driver.find_element(By.NAME, "username")
elem.send_keys("study.ai_172")
elem.send_keys(Keys.ENTER)

elem = driver.find_element(By.NAME,"password")
elem.send_keys("NextPassword172#")
elem.send_keys(Keys.ENTER)
url_list = []
url_list.append(driver.find_elements(By.CLASS_NAME,'js-letter-list-item' ).get_attribute('href'))
letters = []
for i in url_list:
    driver.get(i)
    letter = {
        'author': driver.find_element(By.CLASS_NAME, 'letter-contact').get_attribute('title'),
        'date': driver.find_element(By.CLASS_NAME, 'letter__date').text,
        'name of letter': driver.find_element(By.CLASS_NAME, 'thread-subject').text,
        'text': driver.find_element(By.CLASS_NAME, 'letter-body__body').text
    }
    letters.append(letter)

letters_from_email.insert_many(letters)










