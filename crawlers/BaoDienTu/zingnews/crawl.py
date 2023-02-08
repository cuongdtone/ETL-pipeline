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

db = ConnectDB()
config = yaml.load(open('settings.yaml', 'r'), Loader = yaml.FullLoader)
DOMAIN = config['DOMAIN']
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
}

def crawl_detail(post_url, category):
    try:
        res = requests.get(post_url, headers=headers)
        soup = BeautifulSoup(res.text,'html.parser')
        # print(post_url)
        name_title = ''
        url_title = ''
        content = ''
        tags = []

        idx = post_url.rfind('.htm')
        r_split = post_url[:idx].rsplit("-")
        id_new = r_split[len(r_split)-1]

        h1_title = soup.find("h1",{"class":"the-article-title"})
        if h1_title != None:
            name_title = h1_title.get_text().strip()

            li_posting = soup.find("li",{"class":"the-article-publish"})
            if li_posting != None:
                strip_li_posting = li_posting.get_text().strip()
                index = strip_li_posting.find(" ",4)
                index_1 = strip_li_posting.find(" ",9)
                posting_date = strip_li_posting[index+1:index_1]

            p_content = soup.find("p",{"class":"the-article-summary"})
            if p_content != None:
                content += p_content.get_text().strip()
                div_content = soup.findAll("div",{"class":"the-article-body"})
                for row_content in div_content:
                    sub_p_content = row_content.findAll("p")
                    for sub_row_content in sub_p_content:
                        if sub_row_content.get("class"):
                            continue
                        sub_content = sub_row_content.get_text().strip()
                        content += sub_content

            p_tags = soup.findAll("p",{"class":"the-article-tags"})
            for row_tag in p_tags:
                row_strong = row_tag.find("strong")
                if row_strong != None:
                    sub_tag = row_strong.get_text().strip()
                    tags.append(sub_tag)
                row_a_tag = row_tag.findAll("a")
                if row_a_tag != None:
                    for sub_row_tag in row_a_tag:
                        sub_tag = sub_row_tag.get_text().rstrip()
                        tags.append(sub_tag)

            created_at = int(datetime.timestamp(datetime.now()))
            post = {}
            post["domain"] = DOMAIN
            post["category"] = category
            post["new_id"] = id_new
            post["title"] = name_title
            post["url"] = post_url
            post["content"] = content
            post["tags"] = tags
            post["posting_date"] = posting_date
            post["created_date"] = created_at

            InsertNews(db, post)

    except Exception as exc :
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tracklog.send(False, f"{DOMAIN}__{'crawl.crawl_detail'}: {post_url}: {exc} - Line: {exc_tb.tb_lineno}")

    
def crawl_url(url_category,name_category):
    try:
        if url_category != DOMAIN:
            index = url_category.find('.html')
            url_new_1 = url_category[:index]+"/trang{0}.html"
        else:
            url_new_1 = None

        page = 0
        while page > -1:
            page +=1
            if url_new_1 != None:
                url_category = url_new_1.format(page)
            
            tracklog.send(True, f"{DOMAIN}__{'Start_Crawl'}: {url_category}")

            res = requests.get(url_category, headers=headers)
            soup = BeautifulSoup(res.text,'html.parser')
            dict_url  = {}

            div_title = soup.findAll("p",{"class":"article-title"})
            for row_title in div_title:
                row_a_title = row_title.find('a')
                if row_a_title == None:
                    continue
                title_new = row_a_title.get_text().strip()
                sub_url= row_a_title['href'].strip()
                url_new = DOMAIN + sub_url
                dict_url[url_new] = title_new
                
            for key_1,value_1 in dict_url.items():
                crawl_detail(key_1,name_category)
            if url_category == DOMAIN or page == 50 or dict_url == {}:
                break
            time.sleep(random.randrange(1, config["SLEEP"]))
    except Exception as exc :
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tracklog.send(False, f"{DOMAIN}__{'crawl.crawl_url'}: {url_category}: {exc} - Line: {exc_tb.tb_lineno}")

def start_crawl():
    try:
        res = requests.get(DOMAIN, headers=headers)
        soup = BeautifulSoup(res.text,'html.parser')
        dict_category = {}
        home = 'Trang chủ'
        dict_category[DOMAIN] = home
        div_nav = soup.find("nav",{"class":"category-menu"})
        li_cate = div_nav.findAll("li",{"class":"parent"})
        for row_cate in li_cate:
            a_cate = row_cate.findAll("a")
            for sub_row_cate in a_cate:
                title_cate = sub_row_cate.get_text().strip()
                sub_url_cate = sub_row_cate['href'].strip()
                url_cate = DOMAIN + sub_url_cate
                dict_category[url_cate] = title_cate

        for key,value in dict_category.items():
            crawl_url(key,value)

    except Exception as exc :
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tracklog.send(False, f"{DOMAIN}__{'crawl.start_crawl'}: {exc} - Line: {exc_tb.tb_lineno}")
    finally:
        tracklog.disconnect()
