

import json
import os
from datetime import date
from datetime import datetime

import requests
import yaml
from bs4 import BeautifulSoup

# from utils.db_handler import ConnectDB, InsertNews
from utils.kafka_handler import KafkaHandler


kafka_db = KafkaHandler()
DOMAIN = os.getenv('DOMAIN')

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
}

# date now
today = date.today()
date_now = today.strftime("%d/%m/%Y")


def parse(url_post, id_post):
    try:
        response = requests.get(url_post, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            name_title = ''
            posting_date = ''
            content = ''
            category = ''
            tags = []

            div_post_date = soup.find("span", {"class": "kbwcm-time"})
            if div_post_date != None:
                sub_post = div_post_date.get_text().strip()
                index = sub_post.find(" ")
                posting_date = sub_post[index + 1:]

            # if date_now == posting_date:
            h1_new = soup.find("h1", {"class": "kbwc-title"})
            if h1_new != None:
                name_title = h1_new.get_text().strip()

            h2_content = soup.find("h2", {"class": "knc-sapo"})
            if h2_content != None:
                sub_content = h2_content.get_text().strip()
                content += sub_content
                div_content = soup.find("div", {"class": "knc-content"})
                if div_content != None:
                    p_content = div_content.findAll("p")
                    for row_p in p_content:
                        if row_p.get("style") == 'text-align: right;':
                            continue
                        sub_content = row_p.get_text().strip()
                        content += sub_content

            category_active = soup.find("li", {"class": "kbwsli active"})
            if category_active != None:
                category = category_active.a["title"]

            li_tag = soup.findAll("li", {"class": "kli"})
            for row_tag in li_tag:
                sub_tag = row_tag.get_text().strip()
                tags.append(sub_tag)

            created_at = int(datetime.timestamp(datetime.now()))

            post = {}
            post["domain"] = DOMAIN
            post["category"] = category
            post["new_id"] = id_post
            post["title"] = name_title
            post["url"] = url_post
            post["content"] = content
            post["tags"] = tags
            post["posting_date"] = posting_date
            post["created_date"] = created_at
            kafka_db.send(post)

    except Exception as exc:
        print(f"{DOMAIN}__{'crawl.parse'}: {exc}")


def crawl_data():
    API_KENH14 = "https://kenh14.vn/timeline/laytinmoitronglist-{0}-1-1-1-1-1-0-1-1-1-1.chn"
    page = 0

    url = API_KENH14.format(page)
    # print(url)
    # tracklog.send(True, f"{DOMAIN}__{'Crawl Data'}: {url}")

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data_list = json.loads(response.text)["data"]

        if len(data_list) != 0:
            soup = BeautifulSoup(data_list, "html.parser")
            list_li = soup.find_all("li", {"class": "knswli need-get-value-facebook clearfix"})

            for li in list_li:
                a_first = li.div.a
                if a_first == None:
                    continue
                url_post = "%s%s" % (DOMAIN, a_first["href"][1:])
                id_post = a_first["newsid"]
                parse(url_post, id_post)


def start_crawl():
    try:
        crawl_data()
    except:
        raise Exception("Message")

