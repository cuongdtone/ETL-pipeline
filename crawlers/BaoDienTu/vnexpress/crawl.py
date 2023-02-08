import requests
import yaml
import sys
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import date
import time, json, random, re

from tracklog import tracklog
from data_access import ConnectDB, InsertNews, InsertComment

db = ConnectDB()
config = yaml.load(open('settings.yaml', 'r'), Loader = yaml.FullLoader)
DOMAIN = config['DOMAIN']
headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
    }

def create_comment(new_id, comment_id, contact_name, content, likes):
    cmt = {}
    cmt["domain"] = config["DOMAIN"]
    cmt["new_id"] = new_id
    cmt["comment_id"] = comment_id
    cmt["contact_name"] = contact_name
    cmt["content"] = content
    cmt["likes"] = likes
    created_at = int(datetime.timestamp(datetime.now()))
    cmt["created_date"] = created_at
    return cmt

def crawl_comment(new_id):
    try:
        comment_id = ''
        contact_name = ''
        content = ''
        likes = 0

        url = "https://usi-saas.vnexpress.net/index/get?offset=0&limit=25&frommobile=0&sort=like&is_onload=1&objectid={0}&objecttype=1&siteid=1000000&categoryid=1001002&sign=4798a4f98a7577b5aa22edfa815894d4&cookie_aid=p2z3y5vmsfc14kdl.1609298569&usertype=4&template_type=1&app_mobile_device=0&title=Ca+Covid-19+to%C3%A0n+c%E1%BA%A7u+g%E1%BA%A7n+83+tri%E1%BB%87u%2C+WHO+k%C3%AAu+g%E1%BB%8Di+ph%C3%A2n+ph%E1%BB%91i+b%C3%ACnh+%C4%91%E1%BA%B3ng+vaccine+-+VnExpress".format(new_id)
        response = requests.get(url, headers = headers)
        data_json = json.loads(response.text)
        data = data_json['data']['items']
        for row in data:
            comment_id = row['comment_id']
            contact_name = row['full_name']
            content = row['content']
            likes = row['userlike']
            cmt = create_comment(new_id, comment_id, contact_name, content, likes)
            InsertComment(db, cmt)

    except Exception as exc :
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tracklog.send(False, f"{DOMAIN}__{'crawl.crawl_comment'}: {url}: {exc} - Line: {exc_tb.tb_lineno}")


def parse(post_url):
    try:
        if post_url != None:
            res = requests.get(post_url, headers = headers)
            soup = BeautifulSoup(res.text,'html.parser')

            # cắt chuổi url để lấy id_new
            # index = post_url.find('.html')
            # index_1 = post_url.find('-42')
            # id_new = post_url[index_1+1:index]

            idx = post_url.rfind('.htm')
            r_split = post_url[:idx].rsplit("-")
            id_new = r_split[len(r_split)-1]
            

            name_title = ''
            url_title = ''
            posting_date = ''
            content = ''
            category = ''
            tags = []
            #lấy category của bài viết
            div_category = soup.find("ul",{"class":"breadcrumb"})
            if div_category != None:
                li_category = div_category.find("li")
                a_category = li_category.find("a")
                category = a_category['title']
            #lấy tiêu đề bài viết.
            div_h1 = soup.find("h1",{"class":"title-detail"})
            if div_h1 != None:
                name_title = div_h1.get_text().strip()
            #lấy posting_date
            div_posting_date = soup.find("span",{"class":"date"})
            if div_posting_date != None:
                sub_posting = div_posting_date.get_text().strip()
                # lấy vị trí để cắt chuổi lấy posting_date
                index = sub_posting.find(" ",4)
                index_1 = sub_posting.find(",",7)
                posting_date = sub_posting[index:index_1]
            # Lấy thẻ p chứa nội dung bài viết
            div_p = soup.findAll("p",{"class":"Normal"})
            for row_p in div_p:
                # Bỏ qua thẻ p không cân thiết
                if row_p.get("style") == "text-align:center;":
                    continue
                sub_content = row_p.get_text().strip()
                content += sub_content

            try:
                # Get tags
                script_text = soup.findAll("script", text=re.compile("dataLayer.push"))
                if len(script_text) >=2:
                    scripts = str(script_text[1])
                    tag_split = scripts.split("dataLayer.push({'articleTags':'")
                    if len(tag_split) > 1:
                        tag = tag_split[1].split("'});dataLayer.push({'tag_id'")[0]
                        if tag != None and tag != '':
                            arr_tag = tag.split(',')
                            for t in arr_tag:
                                tags.append(t.strip())
            except Exception as exc :
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print(f"Error -> get tags: {exc}")

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

            crawl_comment(id_new)

    except Exception as exc :
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tracklog.send(False, f"{DOMAIN}__{'crawl.parse'}: {post_url}: {exc} - Line: {exc_tb.tb_lineno}")

# Hàm lấy url của các bài viết theo category
def crawl_data(url_new):
    try:
        res = requests.get(url_new, headers = headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        div_h3 = soup.findAll("h3")
        for row_h3 in div_h3:
            a_row = row_h3.find("a")
            if a_row == None:
                continue
            post_url = a_row['href']

            parse(post_url)
    except Exception as exc :
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tracklog.send(False, f"{DOMAIN}__{'crawl.crawl_data'}: {url_new}: {exc} - Line: {exc_tb.tb_lineno}")
    
        

# Hàm lấy category chính của trang vnexpress
def start_crawl():
    try:
        res = requests.get(DOMAIN, headers = headers)
        soup = BeautifulSoup(res.text,'html.parser')
        dic_category = {}
        sub_div = soup.findAll("li")
        for row in sub_div:
            a_row = row.find("a")
            if a_row == None:
                continue
            url_category = a_row['href']
            title_category = a_row.get_text().strip()
            sub_url_category = DOMAIN + url_category[1:]

            # Bỏ các category không cần thiết
            if sub_url_category == DOMAIN or title_category == 'Video' or title_category == 'Tất cả' or title_category == 'Góc nhìn' or title_category == 'Hài' or DOMAIN in url_category:
                continue
            
            dic_category[sub_url_category] = title_category
            
        for key, value in dic_category.items():
            for i in range(1, config['TOTAL_PAGE'], 1):
                cat_url = "%s-p%s" % (key, str(i))

                tracklog.send(True, f"{DOMAIN}__{'Start_Crawl'}: {cat_url}")

                crawl_data(cat_url)
                time.sleep(random.randrange(1, config["SLEEP"]))

    except Exception as exc :
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tracklog.send(False, f"{DOMAIN}__{'crawl.start_crawl'}: {exc} - Line: {exc_tb.tb_lineno}")
    finally:
        tracklog.disconnect()