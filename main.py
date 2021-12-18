# coding=utf-8
import requests
from bs4 import BeautifulSoup

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}

core_link = "https://www.tripadvisor.ru"

def parse_links():
    links = []
    for i in range(1, 2):
        url = f'https://www.tripadvisor.ru/Restaurants-g{298483 + i}-Moscow_Central_Russia.html'
        print(url)
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, features="html.parser")
        divs = soup.find_all('div', {'class': 'OhCyu'})
        for div in divs:
            link = div.find('a', attrs={'class': 'bHGqj Cj b'}).get('href')
            links.append(core_link + link)
        return links


def parse_rest_info(link) -> dict:
    result_dict = {}
    response = requests.get(link, headers=headers)
    soup = BeautifulSoup(response.text, features="html.parser")
    rest_name = soup.find('h1', {'class': 'fHibz'}).get_text()
    result_dict['name'] = rest_name
    rest_url = soup.find_all('span', {'class': 'dOGcA Ci Wc _S C fhGHT'}.get('href'))
    for elem in rest_url:
        if (elem.get_text() == 'Веб-сайт'):
            url = elem.get('href')
            result_dict[url] = url

    rest_phone = soup.find_all('a', {'class': 'iPqaD _F G- ddFHE eKwUx'})
    for elem in rest_phone:
        phone = elem.get('href').split(sep=":")
        if len(phone) == 2 and phone[0] == "tel":
            result_dict['phone'] = phone[1]

    rest_address = soup.find('a', {'class': 'fhGHT', 'href': '#MAPVIEW'})
    result_dict['address'] = rest_address

    rest_reviews_num_arr = soup.find('a', {'class': 'dUfZJ'}).get_text.split(sep=" ")
    result_dict['reviews_num'] = rest_reviews_num_arr[0]

    rest_rating_arr = soup.find('svg', {'class': 'RWYkj d H0'}).get('title').split(sep=" ")
    result_dict['rating'] = rest_rating_arr[0]

    print(result_dict)
    return result_dict


def parse_rest_comments(link):
    comments_links_all = []
    next_button_link = link
    comments_result_dict = {}

    while next_button_link is not None:
        # парсим ссылки на все комментарии
        response = requests.get(next_button_link, headers=headers)
        soup = BeautifulSoup(response.text, features="html.parser")
        comments_links_from_page = soup.find_all('a', {'class': 'title'})
        for elem in comments_links_from_page:
            comments_links_all.append(core_link + elem.get('href'))
        next_button_class = soup.find('a', {'class': 'nav next ui_button primary'})
        if next_button_class is None:
            break
        next_button_link = core_link + next_button_class.get('href')
    print(comments_links_all)
    # парсим информацию из каждого комментария
    for current_comment_link in comments_links_all:
        response = requests.get(current_comment_link, headers=headers)
        soup = BeautifulSoup(response.text, features="html.parser")
        comment_text = soup.find('p', {'class': 'partial_entry'})
        if comment_text is not None:
            comments_result_dict["comment_text"] = comment_text.get_text()
        comment_usability = soup.find('span', {'class': 'numHelp emphasizeWithColor'})
        if comment_usability is not None:
            comments_result_dict["comment_usabitily"] = comment_usability.get_text()



if __name__ == '__main__':

    parsed_links = parse_links()

    results_info = []
    results_comments = []
    for link in parsed_links:
        # results_info.append(parse_rest_info(link))
        # results_comments.append(parse_rest_comments(link))
        parse_rest_comments(link)

    print(1)


