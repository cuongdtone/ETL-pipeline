import requests
import yaml
import sys
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import date
import time,json, random
from data_access import ConnectDB, InsertNews, InsertComment
from tracklog import tracklog

db = ConnectDB()
config = yaml.load(open('settings.yaml', 'r'), Loader = yaml.FullLoader)
DOMAIN = config['DOMAIN']

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
}

today = date.today()
date_now = today.strftime("%d/%m/%Y")

def create_comment(new_id, comment_id, contact_name, cmt_content, likes):
    cmt = {}
    cmt["domain"] = config["DOMAIN"]
    cmt["new_id"] = new_id
    cmt["comment_id"] = comment_id
    cmt["contact_name"] = contact_name
    cmt["content"] = cmt_content
    cmt["likes"] = likes
    created_at = int(datetime.timestamp(datetime.now()))
    cmt["created_date"] = created_at
    return cmt

def parse(category, url):
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')

            title = ''
            posting_date = ''
            contents = ''
            tags = []

            get_title = soup.find("h1", {"class": "title f-22 c-3e"})
            if get_title != None:
                title = get_title.get_text().strip()

            get_date = soup.find("span", class_="ArticleDate")
            if get_date != None:
                a = get_date.get_text().strip()
                x = a.index(" ")
                posting_date = a[:x + 1].strip()

            div_content = soup.find("div", {"id": "ArticleContent"})
            if div_content != None:
                first_line = soup.find("div", class_="bold ArticleLead")
                contents += first_line.get_text().strip()

                # Content in <p class="t-j">
                p_content = div_content.find_all("p", {"class": "t-j"})
                if len(p_content) > 0:
                    for row in p_content:
                        contents += row.get_text().strip()
                # Content in <p>
                else:
                    p_content = div_content.find_all("p")
                    for i in range(len(p_content)-1):
                        contents += p_content[i].get_text().strip()

            get_tags = soup.find("ul", class_="clearfix")
            if get_tags != None:
                for tag in get_tags.find_all('a'):
                    tags.append(tag.get_text().strip())

            index_slice = url.rindex("-")
            id_post = url.replace(".html", "")
            new_id = id_post[index_slice + 1:]

            page = 0
            while page > -1:
                page += 1

                son_url = "https://i.vietnamnet.vn/jsx/interaction/getInteraction/data.jsx?objkey=vietnamnet.vn_tuanvietnam_{0}&ordby=like&page={1}".format(new_id, page)
                response = requests.get(son_url, headers=headers)
                data_json = json.loads(str(response.text).replace('retvar=', ''))
                if data_json != None and 'comments' in data_json and data_json['comments'] != None and len(data_json['comments']) > 0:
                    for row in data_json['comments']:
                        comment_id = row['objguid']
                        contact_name = row['fullname']
                        cmt_content = row['content']
                        likes = row['like']

                        comments = create_comment(new_id, comment_id, contact_name, cmt_content, likes)
                        InsertComment(db, comments)

                        if "replies" in row and row["replies"] != None:
                            for row_son in row["replies"]:
                                comment_id = row_son['objguid']
                                contact_name = row_son['fullname']
                                cmt_content = row_son['content']
                                likes = row_son['like']
                                comments = create_comment(new_id, comment_id, contact_name, cmt_content, likes)
                                InsertComment(db, comments)
                else:
                    page = -1


            post = {}
            post['title'] = title
            post["domain"] = config["DOMAIN"]
            post["category"] = category
            post["new_id"] = new_id
            post["url"] = url
            post['posting_date'] = posting_date
            post['content'] = contents
            post['tags'] = tags
            post['created_date'] = int(datetime.timestamp(datetime.now()))

            InsertNews(db, post)

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tracklog.send(False, f"{config['DOMAIN']}__crawl.parse: {url}: {exc} - Line: {exc_tb.tb_lineno}")

def crawl_news(url_category, title_category):
    try:
        index_slice = url_category.index("/vn/")
        category_name = url_category[index_slice+4:-1]
        page = 0
        while page > -1:
            page += 1

            url = "https://vietnamnet.vn/jsx/loadmore/?domain=desktop&c={0}&p={1}&s=15&a=5".format(category_name, page)
            tracklog.send(True, f"{config['DOMAIN']}__Start_Crawl: {url}")
            # print(url)
            response = requests.get(url, headers=headers)
            re_data = response.text.replace("retvar =", "")
            data_json = json.loads(re_data)

            if len(data_json) != 0:
                for row in data_json:
                    parse(title_category, row['link'])
            else:
                break

            # print('===========================================')
            # Delay giữa 2 page
            time.sleep(random.randrange(1, config["SLEEP"]))

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tracklog.send(False, f"{config['DOMAIN']}__crawl.crawl_news: {url}: {exc} - Line: {exc_tb.tb_lineno}")

def start_crawl():
    try:
        res = requests.get(DOMAIN, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')

        dict_category = {}
        div_category1 = soup.find("a", class_="label full5 p-l-25")
        div_category = soup.find_all("a", class_="label full5")


        cat_link1 = DOMAIN + div_category1['href']
        cat_name1 = div_category1['title']
        dict_category[cat_link1] = cat_name1

        for div in div_category:
            cat_link = DOMAIN + div['href'].strip()
            cat_name = div['title']
            dict_category[cat_link] = cat_name

        for key, value in dict_category.items():
            crawl_news(key, value)

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tracklog.send(False, f"{config['DOMAIN']}__crawl.start_crawl: {exc} - Line: {exc_tb.tb_lineno}")
    finally:
        tracklog.disconnect()