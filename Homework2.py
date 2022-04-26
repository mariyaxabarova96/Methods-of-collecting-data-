import time

import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
import pandas as pd
import json

for i in range (10):
    i = 0
    url = 'https://hh.ru/search/vacancy?clusters=true&area=1&ored_clusters=true&enable_snippets=true&salary=&text='\
          f"&page={i}&hhtmFrom=vacancy_search_list"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}
    response = requests.get(url, headers=headers)
    dom = bs(response.text, 'html.parser')
    vacancies = dom.find_all('div', {'class': 'vacancy-serp-item__layout'})
    time.sleep(1)
    vacancy_list = []
    for vacancy in vacancies:
        vacancy_data = {}
        vacancy_name = vacancy.find('a', {'data-qa':'vacancy-serp__vacancy-title'}).getText()

        vacancy_salary = vacancy.find('span', {'data-qa':'vacancy-serp__vacancy-compensation'})

        if vacancy_salary==None:
            min_salary = None
            max_salary = None
            salary_currency = None
        else:
            salary = vacancy_salary.getText().replace('\u202f', '').rsplit(' ')
            if salary[0] == 'до':
                min_salary = None
                max_salary = salary[1]
            if salary[0] == 'от':
                min_salary = salary[1]
                max_salary = None
            else:
                min_salary = salary[0]
                max_salary = salary[2]
            salary_currency = salary[-1]

            #pprint(salary)

        vacancy_url = vacancy.find('a', {'data-qa':'vacancy-serp__vacancy-title'})['href']

        vacancy_city = vacancy.find('div',{'data-qa':'vacancy-serp__vacancy-address'}).getText()
        if vacancy_city == None:
            print('Город не указан')

        vacancy_employer = vacancy.find('a', {'data-qa':'vacancy-serp__vacancy-employer'}).getText().replace('\xa0','')

        vacancy_data['name'] = vacancy_name
        vacancy_data['min_salary'] = min_salary
        vacancy_data['max_salary'] = max_salary
        vacancy_data['currency'] = salary_currency
        vacancy_data['url'] = vacancy_url
        vacancy_data['city'] = vacancy_city
        vacancy_data['employer'] = vacancy_employer
        vacancy_data['resourse'] = 'hh.ru'

        vacancy_list.append(vacancy_data)

    i = i + 1

frame = pd.DataFrame(vacancy_list)
#print(frame)
with open('dz2.json','w') as f:
    f.write(json.dumps(vacancy_list))
pprint(vacancy_list)

