import requests
import yaml
import sys
from data_access import *
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import date
import time, json, random
from tracklog import tracklog

db = ConnectDB()
config = yaml.load(open('settings.yaml', 'r'), Loader = yaml.FullLoader)

DOMAIN = config["DOMAIN"]
headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
    }


list_url = []
list_url_menu_category = []

#date now
today = date.today()
date_now = today.strftime("%d/%m/%Y")

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

# crawl_comment của từng bài báo
def crawl_comment(new_id):
    try:
        chil_cmt = []
        limit = 10
        page = 0
        while page > -1:
            page += 1
            url = "https://id.tuoitre.vn/api/getlist-comment.api?pageindex={0}&pagesize=10&objId={1}&objType=1&sort=1&appKey=lHLShlUMAshjvNkHmBzNqERFZammKUXB1DjEuXKfWAwkunzW6fFbfrhP%2FIG0Xwp7aPwhwIuucLW1TVC9lzmUoA%3D%3D".format(page,new_id)
            response = requests.get(url, headers = headers)

            data_json = json.loads(response.text)
            cmt_json = json.loads(data_json["Data"])
            if cmt_json != None:
                for i in cmt_json:
                    comment_id = ''
                    contact_name = ''
                    content = ''
                    likes = 0

                    comment_id = i['id']
                    contact_name = i['sender_fullname']
                    content = i['content']
                    likes = i['likes']
                    cmt = create_comment(new_id, comment_id, contact_name, content, likes)
                    InsertComment(db, cmt)

                    if chil_cmt != None:
                        for j in chil_cmt:
                            comment_id = j['id']
                            contact_name = j['sender_fullname']
                            content = j['content']
                            likes = j['likes']
                            cmt = create_comment(new_id, comment_id, contact_name, content, likes)
                            InsertComment(db, cmt)
                    
                if len(cmt_json) < limit:
                    break
            else:
                break
    except Exception as exc :
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tracklog.send(False, f"{DOMAIN}__crawl.crawl_comment: {url}:s {exc} - Line: {exc_tb.tb_lineno}")

#Lấy chi tiết của từng bài viết
def parse(url_post):
    try:
        new_id = ''
        category = ''
        name_title = ''
        url_title = ''
        posting_date = ''
        content = ''
        tags = []

        res = requests.get(url_post, headers=headers)
        soup = BeautifulSoup(res.text,'html.parser')
        #lấy thời gian đăng bài
        div_posting_time = soup.find("div", {"class":"date-time"})
        if div_posting_time != None:
            str_posting = div_posting_time.get_text().strip()
            index = str_posting.find(" ")
            posting_date = str_posting[:index]
        else:
            posting_date = int(datetime.timestamp(datetime.now()))
        
        # nếu bài viết đăng ngày hôm trước thì không lấy
        # if (date_now != posting_date):
        #     return
        
        #lấy category của bài viết 
        div_category = soup.find("div",{"class":"bread-crumbs"})
        if div_category != None:
            a_category = div_category.find("a")
            category = a_category['title']
        #lấy tiêu đề của bài báo
        div_title = soup.findAll("div",{"class":"content-detail"})
        for row_title in div_title:
            title_name = row_title.find("h1",{"class":"article-title"})
            name_title = title_name.get_text().strip()
        #lấy nội dung của bài viết
        div_content = soup.findAll("div",{"class":"content fck"})
        for row_content in div_content:
            p = row_content.findAll("p")
            for sub_row_content in p:
                sub_content = sub_row_content.get_text().strip()
                # Bỏ qua các thẻ p dư thừa
                index_2 = sub_content.find('Ảnh')
                index_3 = sub_content.find('TTO')
                index_4 = sub_content.find('Nguồn')
                if index_2 > -1 or index_3 > -1 or index_4 > -1:
                    continue
                content += sub_content
        #lấy các thẻ tag của bài viết
        div_tag = soup.findAll("div",{"class":"tags-container"})
        for row_tag in div_tag:
            cat_tag = row_tag.findAll("a")
            for sub_row_tag in cat_tag:
                tag_name = sub_row_tag["title"]
                tag_url = sub_row_tag["href"]
                tags.append(tag_name)

        #cắt chuổi url của bài viết để lấy ID
        idx = url_post.rfind('.htm')
        r_split = url_post[:idx].rsplit("-")
        new_id = r_split[len(r_split)-1]


        createdAt = int(datetime.timestamp(datetime.now()))

        post = {}
        post["domain"] = DOMAIN
        post["category"] = category
        post["new_id"] = new_id
        post["title"] = name_title
        post["url"] = url_post
        post["content"] = content
        post["tags"] = tags
        post["posting_date"] = posting_date
        post["created_date"] = createdAt

        InsertNews(db, post)
        # goi ham get comments
        crawl_comment(new_id)
    
    except Exception as exc :
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tracklog.send(False, f"{DOMAIN}__{'crawl.parse'}: {url_post}: {exc} - Line: {exc_tb.tb_lineno}")

#Lấy ra tất cả url theo từng category
def crawl_data(url_category):
    try:
        page = 0
        if url_category == "https://tuoitre.vn/" or url_category == "https://congnghe.tuoitre.vn" or url_category == "https://dulich.tuoitre.vn" or url_category == "https://thethao.tuoitre.vn":
            url_new = None
        else:
            index = url_category.find('.htm')
            url_new = url_category[:index]+"/trang-{0}.htm"

        while page > -1:
            page += 1
            if url_new != None:
                url_category = url_new.format(page)

            tracklog.send(True, f"{DOMAIN}__{'Start_Crawl'}: {url_category}")
            res = requests.get(url_category, headers=headers)

            soup = BeautifulSoup(res.text,'html.parser')

            #Danh sách url của category
            list_url= []
            # Biến tạm để lấy url con 
            sub_url = ''

            # Lấy ra url bài viết chính của các bài viết còn lại
            div_new = soup.findAll("div",{"class":"w664"})
            if div_new != None:
                for row_new in div_new:
                    # bài viết chính đều là thẻ h2 nên để tên vậy
                    h2_main = row_new.findAll("h2")
                    for sub_row_new in h2_main:
                        a_main = sub_row_new.find("a")
                        if a_main == None:
                            continue
                        name_title = a_main['title']
                        sub_url = a_main['href']
                        url_title = DOMAIN + sub_url[1:]
                        list_url.append(url_title)
                # Lấy ra url của các bài viết còn lại
                div_h3 = soup.findAll('h3',{"class":"title-news"})
                for row_h3 in div_h3:
                    a_row = row_h3.find('a')
                    if a_row == None:
                        continue
                    name_title = a_row.get_text().strip()
                    sub_url = a_row['href']
                    url_title = DOMAIN + sub_url[1:] 
                    list_url.append(url_title)

            # code danh cho 2 trang du lịch, thể thao
            div_new_1 = soup.findAll("div",{"class":"highlight"})   
            if div_new_1 != []:
                for row_new in div_new_1:
                    a_main = row_new.findAll("a",{"data-linktype":"newsdetail"})
                    for sub_row_new in a_main:
                        name_title = sub_row_new["title"]
                        sub_url = sub_row_new['href']
                        url_title = DOMAIN + sub_url[1:]
                        list_url.append(url_title)

                #lấy ra url của các bài viết còn lại
                div_h3 = soup.findAll('h3')
                for row_h3 in div_h3:
                    a_row = row_h3.find("a")
                    if a_row == None:
                        continue
                    name_title = a_row["title"]
                    sub_url = a_row['href']
                    url_title = DOMAIN + sub_url[1:]
                    if not url_title in list_url:
                        list_url.append(url_title)

            if page == 100:
                break
            for url in list_url:
                parse(url)

            if url_category == "https://tuoitre.vn/" or url_category == "https://congnghe.tuoitre.vn" or url_category == "https://dulich.tuoitre.vn" or url_category == "https://thethao.tuoitre.vn":
                break
            
            time.sleep(random.randrange(1, config["SLEEP"]))

    except Exception as exc :
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tracklog.send(False, f"{DOMAIN}__{'crawl.crawl_data'}: {url_category}: {exc} - Line: {exc_tb.tb_lineno}")


#get category
def start_crawl():
    try:
        res = requests.get(DOMAIN, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')

        div_menu_category = soup.findAll("div",{"class":"header-bottom"})

        dic_category = {}
        for row_category in div_menu_category:
            ul_cat = row_category.findAll("ul",{"class":"menu-ul"})
            for sub_category in ul_cat:
                a_category = sub_category.findAll('a')
                for sub_sub_category in a_category:
                    title_category = sub_sub_category['title']
                    url_category = sub_sub_category['href']
                    index = url_category.find('https')
                    #bỏ qua thẻ Media
                    if title_category == "Media":
                        continue
                    if index > -1:
                        dic_category[url_category] = title_category
                    else:
                        sub_url = DOMAIN + url_category[1:]
                        dic_category[sub_url] = title_category

        for key, value in dic_category.items():
            crawl_data(key)
    
    except Exception as exc :
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tracklog.send(False, f"{DOMAIN}__{'crawl.start_crawl'}: {exc} - Line: {exc_tb.tb_lineno}")
    finally:
        tracklog.disconnect()