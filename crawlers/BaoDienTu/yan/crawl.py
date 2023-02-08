import requests
import yaml
import sys
from data_access import ConnectDB, InsertNews
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import date
import time
import random
from tracklog import tracklog

config = yaml.load(open('settings.yaml', 'r'), Loader = yaml.FullLoader)
DOMAIN = config['DOMAIN']
db = ConnectDB()

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
}

def crawl_detail(post_url, category):
    try:
        res = requests.get(post_url, headers = headers)
        soup = BeautifulSoup(res.text,'html.parser')

        name_title = ''
        posting_date = ''
        content = ''
        sub_content = ''
        tags = []

        idx = post_url.rfind('.htm')
        r_split = post_url[:idx].rsplit("-")
        id_new = r_split[len(r_split)-1]

        h1_title = soup.find("h1",{"class":"detail-title"})
        if h1_title != None:
            name_title = h1_title.get_text().strip()

        p_post = soup.find("p",{"class":"detail-info"})
        if p_post != None:
            date_post = p_post.get_text().strip()
            index = date_post.find(",")
            posting_date = date_post[:index]

        h2_content = soup.find("h2",{"class":"des"})
        if h2_content != None:
            sub_content = h2_content.get_text().strip()
            content += sub_content

        div_content = soup.find("div",{"id":"contentBody"})
        if div_content != None:
            p_content = div_content.findAll("p",{"class":None})
            for row_p in p_content:
                sub_content = row_p.get_text().strip()
                content += sub_content

        url = "https://www.yan.vn/ContentList/GetLoadMoreV6/?nameLoadMore=Tag&zoneId=1&p=1&mobile=false&contentId={0}".format(id_new)
        response = requests.get(url, headers = headers)
        soup_1 = BeautifulSoup(response.text,'html.parser')
        div = soup_1.findAll("div",{"class":"item"})
        for row_tag in div:
            sub_tag = row_tag.get_text().strip()
            tags.append(sub_tag)
        createdAt = int(datetime.timestamp(datetime.now()))
        post = {}
        post["domain"] = DOMAIN
        post["category"] = category
        post["new_id"] = id_new
        post["title"] = name_title
        post["url"] = post_url
        post["content"] = content
        post["tags"] = tags
        post["posting_date"] = posting_date
        post["created_date"] = createdAt

        InsertNews(db, post)

    except Exception as exc :
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tracklog.send(False, f"{DOMAIN}__{'crawl.crawl_detail'}: {post_url}__{exc} - Line: {exc_tb.tb_lineno}")
    
def crawl_url(id_cate, name_category):
    try:
        page = 0
        count = 0
        dict_url = {}
        while page > -1:
            page += 1

            url = "https://www.yan.vn/ContentList/TinMoiLoadMore?id={0}&cat=0&mobile=false&LoadMore={1}".format(id_cate, page)
            tracklog.send(True, f"{DOMAIN}__{'Start_Crawl'}: {url}")

            response = requests.get(url, headers = headers)
            soup_1 = BeautifulSoup(response.text,'html.parser')
            # print(soup_1)
            h3_new = soup_1.findAll("h3",{"class":"m-0"})
            for row_h3 in h3_new:
                a_h3 = row_h3.find("a")
                if a_h3 == None:
                    continue
                title = a_h3.get_text().strip()
                sub_url = a_h3['href']
                url = DOMAIN + sub_url
                dict_url[url] = title
            if len(dict_url) == count:
                break
            else:
                count = len(dict_url)

            for key,value in dict_url.items():
                crawl_detail(key, name_category)

            time.sleep(random.randrange(1, config["SLEEP"]))
    except Exception as exc :
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tracklog.send(False, f"{DOMAIN}__{'crawl.crawl_url'}: {url}: {exc} - Line: {exc_tb.tb_lineno}")

def start_crawl():
    try:
        Home = "Trang Chủ"
        id_cate = 0
        
        res = requests.get(DOMAIN, headers = headers)
        soup = BeautifulSoup(res.text,'html.parser')
        dict_category = {}
        dict_category[id_cate] = Home
        div_cate = soup.find("ul",{"class":"main-menu"})
        li_cate = div_cate.findAll("li")
        for row_cate in li_cate:
            a_cate = row_cate.find("a")
            if a_cate != None:
                category_name = a_cate.get_text().strip()
                if category_name == 'VIDEO':
                    continue
                category_url = a_cate['href']
                index = category_url.rfind('-')
                id_cate = category_url[index+1:len(category_url)-1]
                dict_category[id_cate] = category_name

        div_col = soup.findAll("div",{"class":"col-md-3"})
        for row_col in div_col:
            li_col = row_col.findAll("li")
            for sub_col in li_col:
                a_col = sub_col.find("a")
                if a_col != None:
                    category_name = a_col.get_text().strip()
                    if category_name == 'VIDEO':
                        continue
                    category_url = a_col['href']
                    index = category_url.rfind('-')
                    id_cate = category_url[index+1:len(category_url)-1]
                    dict_category[id_cate] = category_name

        for key,value in dict_category.items():
            crawl_url(key, value)
            

    except Exception as exc :
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tracklog.send(False, f"{DOMAIN}__{'crawl.start_crawl'}__{exc} - Line: {exc_tb.tb_lineno}")
    finally:
        tracklog.disconnect()