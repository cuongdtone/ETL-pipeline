import os
from datetime import datetime
import os
import random
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from utils.data_access import DataHandler

db = DataHandler()
DOMAIN = os.getenv('DOMAIN')

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
}


def parse(category, url):
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')

        new_id = ''
        name_title = ''
        url_title = ''
        posting_date = ''
        content = ''
        tags = []

        div_post = soup.find("div", {"class": "dt-news__meta"})
        if div_post != None:
            span_post = div_post.find("span")
            if span_post != None:
                sub_posting = span_post.get_text().strip()
                index = sub_posting.find(" ", 4)
                posting_date = sub_posting[index + 1: index + 11]

        # if date_now != posting_date:
        #     return

        idx = url.rfind('.htm')
        r_split = url[:idx].rsplit("-")
        new_id = r_split[len(r_split) - 1]

        div_name_title = soup.find("h1", {"class": "dt-news__title"})
        if div_name_title != None:
            name_title = div_name_title.get_text().strip()

        div_h2 = soup.find("h2")
        if div_h2 != None:
            sub_content = div_h2.get_text().strip()
            content += sub_content
            div_content = soup.find("div", {"class": "dt-news__content"})
            if div_content != None:
                p_content = div_content.findAll("p")
                for row_content in p_content:
                    if row_content.get('style'):
                        continue
                    sub_content = row_content.get_text().strip()
                    content += sub_content

        div_tags = soup.findAll("h4", {"class": "dt-news__tag"})
        for row_tag in div_tags:
            a_tag = row_tag.find("a")
            if a_tag != None:
                sub_tag = a_tag['title']
                tags.append(sub_tag)

        created_at = int(datetime.timestamp(datetime.now()))
        post = {}
        post["domain"] = DOMAIN
        post["category"] = category
        post["new_id"] = new_id
        post["title"] = name_title
        post["url"] = url
        post["content"] = content
        post["tags"] = tags
        post["posting_date"] = posting_date
        post["created_date"] = created_at

        db.put(post)
    except Exception as exc:
        print(f"{DOMAIN}__{'crawl.parse'}: {url}__{exc}")


def crawl_detail_url(title_category, url_category):
    try:
        res = requests.get(url_category, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        list_url = []

        div_h2 = soup.findAll("h2", {"class": "news-item__title"})
        for row_div_h2 in div_h2:
            a_row = row_div_h2.find("a")
            if a_row == None:
                continue
            url = a_row['href']
            sub_url = DOMAIN + url[1:]
            list_url.append(sub_url)

        div_h3 = soup.findAll("h3", {"class": "news-item__title"})
        for row_div_h3 in div_h3:
            a_row = row_div_h3.find("a")
            if a_row == None:
                continue
            url = a_row['href']
            sub_url = DOMAIN + url[1:]

            if not sub_url in list_url:
                list_url.append(sub_url)

        for url_detail in list_url:
            # print(url_detail)
            parse(title_category, url_detail)

    except Exception as exc:
        print(f"{DOMAIN}__{'crawl.crawl_detail_url'}: {url_category}: {exc}")


# get category của dân trí
def start_crawl(**kwargs):
    try:
        res = requests.get(DOMAIN, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')

        dict_category = {}

        div_category = soup.findAll("li", {"class": "dropdown"})
        print(div_category)
        for row in div_category:
            parent_a_row = row.findAll("a")

            for sub_row in parent_a_row:
                sub_a_row = sub_row.get_text().strip()
                if sub_a_row == 'Video' or sub_a_row == "English" or sub_a_row == 'Fica' or sub_a_row == 'Hương vị Việt' or sub_a_row == 'Bảng giá ô tô' or sub_a_row == 'Giá xe' or sub_a_row == 'Sắc màu Nhật Bản':
                    continue

                url_category = sub_row['href']
                sub_url = DOMAIN + url_category[1:]

                dict_category[sub_url] = sub_a_row

        for key, value in dict_category.items():
            for i in range(1, 10):
                cat_url = key.replace(".htm", "/trang-%s.htm" % str(i))
                # print(cat_url)

                print(f"{DOMAIN}__{'Start_Crawl'}: {cat_url}")
                crawl_detail_url(value, cat_url)

                # Delay giữa 2 page
                time.sleep(random.randrange(1, int(os.getenv('SLEEP'))))
    except Exception as exc:
        print(f"{DOMAIN}__{'crawl.start_crawl'}: {exc}")

