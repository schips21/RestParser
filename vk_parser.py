import time

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}

def parse_one_post_info(url, com_id):
    parsed_comments = []
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, features="html.parser")
    tmp_post = soup.find('div', {'class': 'wall_post_text'})
    post = tmp_post.get_text()
    tmp_date = soup.find_all('span', {'class': 'rel_date'})
    date = tmp_date[0].get_text()
    views = soup.find('span', {'class': '_views'}).get_text()
    reposts_count = soup.find_all('span', {'class': 'PostBottomAction__count _like_button_count _counter_anim_container PostBottomAction__count--withBg'})[1].get_text()
    reaction_count = soup.find_all('div', {'class': 'ReactionsPreview__count _counter_anim_container'})[0].get_text()


    tmp_parsed_comments = soup.find_all('div', {'class': 'wall_reply_text'})
    comments_count = 0
    for comm in tmp_parsed_comments:
        parsed_comments.append(comm.get_text())
        final_comments.append([com_id, id_post, comm.get_text()])
        com_id += 1
        comments_count += 1

    final_posts.append([id_post, url, post, date, views, comments_count, reposts_count, reaction_count])
    print(post)
    return com_id


if __name__ == '__main__':
    sber_link_pages = 'https://vk.com/wall-22522055?own=1'
    init_vk_link = 'https://vk.com'

    sber_coms_text = []
    response = requests.get(sber_link_pages, headers=headers)
    soup = BeautifulSoup(response.text, features="html.parser")

    # ссылки на посты с одной страницы
    links_for_posts_from_one_page = []
    tmp_links_for_posts_from_one_page = soup.find_all('a', {'class': 'post_link'})

    final_posts = []
    final_comments = []
    id_post = 0
    id_comm = 0
    for link in tmp_links_for_posts_from_one_page:
        if ('https://' in link.get('href')):
            continue
        links_for_posts_from_one_page.append(init_vk_link + link.get('href'))
        id_comm = parse_one_post_info(init_vk_link + link.get('href'), id_comm)
        id_post += 1

    df_posts = pd.DataFrame(final_posts, columns=['id', 'url', 'post', 'date', 'views', 'comments_count', 'reposts_count', 'reaction_count'])
    df_posts.to_csv('posts.csv', mode='a', header=False, index=False)

    df_comments = pd.DataFrame(final_comments, columns=['id', 'post_id', 'comment_text'])
    df_comments.to_csv('comments.csv', mode='a', header=False, index=False)

