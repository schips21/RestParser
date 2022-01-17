# coding=utf-8
import csv

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}


def parse_links_for_all_rests():
    # links = []
    next_button_link = init_link
    while next_button_link is not None:
        # парсим ссылки на все рестораны
        response = requests.get(next_button_link, headers=headers)
        soup = BeautifulSoup(response.text, features="html.parser")
        rest_links_from_page = soup.find_all('a', {'class': 'bHGqj Cj b'})
        for elem in rest_links_from_page:
            parsed_links_for_all_rests.append(core_link + elem.get('href'))
        next_button_class = soup.find('a', {'class': 'nav next rndBtn ui_button primary taLnk'})
        if next_button_class is None:
            break
        next_button_link = core_link + next_button_class.get('href')
        print(next_button_link)
        if len(parsed_links_for_all_rests) > 10000:
            break


def parse_rest_info(link) -> bool:
    result_dict = {}
    response = requests.get(link, headers=headers)
    soup = BeautifulSoup(response.text, features="html.parser")
    if soup.find('h1', {'class': 'fHibz'}) is None:
        return False
    rest_name = soup.find('h1', {'class': 'fHibz'}).get_text()
    result_dict['name'] = rest_name

    # rest_url_arr = soup.find_all('a', {'class': 'dOGcA Ci Wc _S C fhGHT'}, href=True)
    # rest_url = ''
    # for elem in rest_url_arr:
    #     if elem.get_text() == 'Веб-сайт':
    #         rest_url = elem.get('href')
    #         result_dict['url'] = rest_url
    #         break
    rest_url = link
    result_dict['url'] = rest_url

    rest_phone_arr = soup.find_all('a', {'class': 'iPqaD _F G- ddFHE eKwUx'})
    rest_phone = ''
    for elem in rest_phone_arr:
        phone = elem.get('href').split(sep=":")
        if len(phone) == 2 and phone[0] == "tel":
            rest_phone = phone[1]
            result_dict['phone'] = rest_phone

    rest_address_found = soup.find('a', {'class': 'fhGHT', 'href': '#MAPVIEW'})
    rest_address = ''
    if rest_address_found is not None:
        rest_address = rest_address_found.get_text()
        result_dict['address'] = rest_address

    rest_reviews_num = ''
    rest_reviews_num_found = soup.find('a', {'class': 'dUfZJ'})
    if rest_reviews_num_found is not None:
        rest_reviews_num_arr = rest_reviews_num_found.get_text().split(sep=" ")
        rest_reviews_num = rest_reviews_num_arr[0]

    rest_rating = ''
    rest_rating_found = soup.find('svg', {'class': 'RWYkj d H0'})
    if rest_rating_found is not None:
        rest_rating_arr = rest_rating_found.get('title').split(sep=" ")
        rest_rating = rest_rating_arr[0]

    results_restaurants.append(
        [rest_name, rest_url, rest_phone, rest_address, rest_reviews_num, rest_rating])
    parse_rest_comments(link)
    print(result_dict)
    return True
    # return result_dict


def parse_rest_comments(link):
    # id_comment = 1
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
    # print(comments_links_all)
    # парсим информацию из каждого комментария
    for current_comment_link in comments_links_all:
        response = requests.get(current_comment_link, headers=headers)
        soup = BeautifulSoup(response.text, features="html.parser")
        comment_text = soup.find('p', {'class': 'partial_entry'})
        if comment_text is not None:
            comment_text_final = comment_text.get_text()
            comments_result_dict["comment_text"] = comment_text.get_text()
        comment_usability = soup.find('span', {'class': 'numHelp emphasizeWithColor'})
        if comment_usability is not None:
            comment_numbers = re.findall('\d+', comment_usability.get_text())
            if len(comment_numbers) == 0:
                comment_usability_final = 0
            else:
                comment_usability_final = int(comment_numbers[0])
            comments_result_dict["comment_usability"] = comment_usability_final
        else:
            comment_usability_final = 0
        comment_date = soup.find_all('span', {'class': 'ratingDate relativeDate'})
        if comment_date is not None and comment_date.__len__() > 0:
            comment_date_final = comment_date[0].get('title')
        results_comments.append([rest_id, comment_text_final, comment_usability_final, comment_date_final])
        # id_comment = id_comment + 1
        comment_text_final = ''
        comment_usability_final = ''
        comment_date_final = ''


if __name__ == '__main__':
    core_link = "https://www.tripadvisor.ru"
    init_link = core_link + '/Restaurants-g665311-Tolyatti_Samara_Oblast_Volga_District.html '
    parsed_links_for_all_rests = []
    results_comments = []
    results_restaurants = []

    parse_links_for_all_rests()
    df_rest_links = pd.DataFrame(parsed_links_for_all_rests, columns=['link'])
    df_rest_links.to_csv('rest_links.csv', index=False, header=False)
    print('Ссылки на рестораны успешно собраны')

    rest_id = 8051
    try:
        for link in parsed_links_for_all_rests:
            print('Собираем данные о ресторане № ' + rest_id.__str__() + ' ' + link)
            if parse_rest_info(link) is False:
                continue
            print('Данные о ресторане № ' + rest_id.__str__() + ' успешно собраны')
            rest_id = rest_id + 1
            df_restaurants = pd.DataFrame(results_restaurants,
                                          columns=['rest_name', 'rest_url', 'rest_phone', 'rest_address', 'rest_reviews_number', 'rest_rating'])
            # df_restaurants.index.rename('id_restaurant', inplace=True)
            df_comments = pd.DataFrame(results_comments, columns=['id_restaurant', 'comment_text', 'comment_usability', 'comment_date'])
            # df_comments.index.rename('id_comment', inplace=True)
            df_restaurants.to_csv('restraunts_info.csv', mode='a', header=False, index=True)
            df_comments.to_csv('comments.csv', mode='a', header=False, index=True)
            results_comments = []
            results_restaurants = []

    except BaseException:
        print('Error' + BaseException)


#
#     try:
#         parse_rest_info(
#             'https://www.tripadvisor.ru/Restaurant_Review-g298484-d8344415-Reviews-Auran-Moscow_Central_Russia.html')
#     except BaseException:
#         print('Error')
# parse_rest_comments(
#     'https://www.tripadvisor.ru/Restaurant_Review-g298484-d8344415-Reviews-Auran-Moscow_Central_Russia.html')
