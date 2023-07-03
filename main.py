import requests
import fake_headers
import bs4
from bs4 import BeautifulSoup
import lxml
from time import sleep
import json

headers = fake_headers.Headers(browser="firefox", os="win")
headers_dict = headers.generate()

def get_url_vacancy():
    for count in range(1, 5):

        sleep(2)
        url = f"https://spb.hh.ru/search/vacancy?text=python&area=1&area=2&page{count}"

        response = requests.get(url, headers=headers_dict)

        soup = bs4.BeautifulSoup(response.text, "lxml")

        main_tag = soup.find("main", class_="vacancy-serp-content")
        div_results_tag = main_tag.find("div", id="a11y-main-content")
        a_tag_urls = div_results_tag.find_all('a', class_='serp-item__title')

        for i in a_tag_urls:
            all_url_vacancy = i["href"]

            yield all_url_vacancy

# list_of_urls = []
# for item in all_url_vacancy:
#     url = item.get("href")
#     list_of_urls.append(url)

# all_vacancies = div_results_tag.find_all('div', class_='vacancy-serp-item-body__main-info')
#
vacancies = []

for all_url_vacancy in get_url_vacancy():

    response = requests.get(all_url_vacancy, headers=headers_dict)
    soup = bs4.BeautifulSoup(response.text, "lxml")

    data = soup.find("div", id="a11y-main-content")   # почему-то перестало забирать информацию из тега, но до этого программа работала

    tags = soup.find_all('span', class_='bloko-tag__section bloko-tag__section_text')
    tags_list = []
    for tag in tags:
        tags_list.append(tag.text)

    if 'Django' in tags_list or 'Flask' in tags_list:
        url = data.find('a', class_='serp-item__title').get('href')
        salary = data.find('span', class_='bloko-header-section-3')
        organization = data.find('div', class_='vacancy-serp-item__meta-info-company')
        city = list(data.find(class_='vacancy-serp-item__info').children)

        if salary != None:
            salary = salary.text.replace('\u202f', ' ')

            vacancies.append(
                    {
                        'url': url,
                        'salary': salary,
                        'organization': organization.text.replace('\xa0', ' '),
                        'city': city[1].text,
                        'tags': tags_list,
                    }
                )

with open('json_vacansies.json', 'w') as f:
    json.dump(vacancies, f, indent=2, ensure_ascii=False)

