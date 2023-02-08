import requests
import yaml
import sys
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import date
from data_access import ConnectDB, InsertNews, InsertComment
from tracklog import tracklog
import time, random

config = yaml.load(open('settings.yaml', 'r'), Loader = yaml.FullLoader)
DOMAIN = config['DOMAIN']

headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    }

today = date.today()
date_now = today.strftime("%d/%m/%Y")

db = ConnectDB()

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

def crawl_comment(new_id):
    pass


def parse(category, url):
    try:
        title = ''
        posting_date = ''
        contents = ''
        tags = []

        req = requests.get(url, headers=headers)
        soup = BeautifulSoup(req.text, "html.parser")

        get_title = soup.find("h1", class_="details__headline")
        if get_title != None:
            title = get_title.get_text().strip()

        get_time = soup.find("time")
        if get_time != None:
            a = get_time.get_text().strip()
            x = a.rindex("-")
            posting_date = a[x + 1:]

        get_contents1 = soup.find("div", id="chapeau")
        get_contents2 = soup.find("div", class_="cms-body detail")
        if get_contents1 and get_contents2 != None:
            contents = get_contents1.get_text().strip() + get_contents2.get_text().strip()

        get_tags = soup.find("div", class_="details__tags")
        if get_tags != None:
            for tag in get_tags.find_all('a'):
                tags.append(tag.get_text().strip())

        index_slice = url.rindex("-")
        id = url.replace(".html", "")
        new_id = id[index_slice + 1:]
#======================================================================

        get_comments = soup.find_all("div", class_="usercomment")
        if get_comments != None:
            for cmt in get_comments:
                comment_id = cmt['rel']
                contact_name = cmt.find('h4').get_text()
                cmt_content = cmt.get_text().strip()
                likes = int(cmt['data-likes'])
                # h4_contact_name = cmt.find('h4')
                # div_content = cmt.find('div', class_='comment')
                comments = create_comment(new_id, comment_id, contact_name, cmt_content, likes)
                InsertComment(db, comments)

#=======================================================================

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
        # print(post)
        InsertNews(db, post)

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tracklog.send(False, f"{DOMAIN}__{'crawl.parse'}: {url}: {exc} - Line: {exc_tb.tb_lineno}")

def crawl_news(title_category, url_category):
    try:
        for i in range(1, config['TOTAL_PAGE'], 1):
            cat_url = "%strang-%s.html" % (url_category, str(i))

            tracklog.send(True, f"{DOMAIN}__{'Start_Crawl'}: {cat_url}")

            list_url = []

            response = requests.get(cat_url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")

            get_link = soup.find_all("a", class_="story__thumb")
            for post_url in get_link:
                if "thanhnien" not in post_url['href']:
                    url = DOMAIN + post_url['href']
                    if url not in list_url:
                        list_url.append(url)

            for url_detail in list_url:
                parse(title_category, url_detail)
                # Delay giữa 2 bài viết
            
            time.sleep(random.randrange(1, config["SLEEP"]))

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tracklog.send(False, f"{DOMAIN}__{'crawl.crawl_news'}: {cat_url}: {exc} - Line: {exc_tb.tb_lineno}")


def start_crawl():
    try:
        res = requests.get(DOMAIN, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')

        dict_category = {}

        div_category = soup.find_all("a", class_="global-navigation__title")
        for link in div_category:
            if "video" in link['href']:
                continue
            cat_link = ''
            cat_name = link['title']
            if 'thanhnien' not in link['href']:
                cat_link = DOMAIN + link['href']
            else:
                cat_link = link['href']
            dict_category[cat_link] = cat_name

        for key, value in dict_category.items():
            crawl_news(value, key)

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tracklog.send(False, f"{DOMAIN}__{'crawl.start_crawl'}: {exc} - Line: {exc_tb.tb_lineno}")
    finally:
        tracklog.disconnect()