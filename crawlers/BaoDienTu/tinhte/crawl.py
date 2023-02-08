import requests
import yaml
import time
from datetime import datetime
from bs4 import BeautifulSoup
from data_access import *
from tracklog import tracklog
import sys

db = ConnectDB()
config = yaml.load(open('settings.yaml', 'r'), Loader=yaml.FullLoader)
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
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


def parse_comment(list_comment, id_post, url):
    try:
        for cmt in list_comment:
            cmt_id = cmt["id"].replace("post-", "")

            contact_name = ""
            a_contact_name = cmt.find("a", {"class": "author-name"})
            if a_contact_name != None:
                contact_name = a_contact_name.get_text().strip()
            else:
                a_contact_name = cmt.find("a", {"class": "author-name"})
                if a_contact_name != None:
                    contact_name = a_contact_name.get_text().strip()

            content = ""
            cmt_content = cmt.find("span", {"class": "xf-body-paragraph"})
            if cmt_content != None:
                content = cmt_content.get_text().strip()
            else:
                cmt_content = cmt.find("div", {"class": "xfBody"})
                if cmt_content != None:
                    content = cmt_content.get_text().strip()

            like_container = cmt.next_sibling
            if like_container != None:
                list_user_like = like_container.find_all("span")
                total_like = 0
                if len(list_user_like) != 0:
                    last_index = len(list_user_like) - 1
                    last_span = list_user_like[last_index]
                    if last_span != None:
                        check_last_like = last_span.get_text().strip()

                    if check_last_like == "thích nội dung này":
                        total_like = last_index
                    else:
                        people_like = check_last_like.replace(" người khác thích nội dung này", "").replace("và ", "")
                        total_like = last_index + int(people_like)
                likes = total_like

            comment = create_comment(id_post, cmt_id, contact_name, content, likes)
            InsertComment(db, comment)

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        #print("parse_comment error:", exc)
        tracklog.send(False, f"{config['DOMAIN']}__crawl.parse_comment: {url}: {exc} - Line: {exc_tb.tb_lineno}")

def crawl_comment(url_post, id_post):
    try:
        page = 0
        while page > -1:
            page += 1
            url = "%spage-%s" % (url_post, str(page))
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                list_cmt_lv1 = soup.find_all("div", {"class": "thread-comment__box"})
                if len(list_cmt_lv1) != 0:
                    parse_comment(list_cmt_lv1, id_post, url)

                list_cmt_lv2 = soup.find_all("div", {"class": "thread-comment__box"})
                if len(list_cmt_lv2) != 0:
                    parse_comment(list_cmt_lv2, id_post, url)

                check_break = soup.find("div", {"class": "error-page"})

                if check_break != None:
                    break
            else:
                break

    except Exception as exc:
        # print("crawl_comment error:", exc)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tracklog.send(False, f"{config['DOMAIN']}__crawl.crawl_comment: {url}: {exc} - Line: {exc_tb.tb_lineno}")

def parse(list_post, category_name, total_page):
    try:
        if len(list_post) != 0:
            length_page = 0

            for row in list_post:
                url_post = "%s%s" % (config["DOMAIN"], row["href"])
                response = requests.get(url_post, headers=headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    post = {}
                    post["domain"] = config["DOMAIN"]
                    post["category"] = category_name
                    post["url"] = url_post

                    index_slice = url_post.rindex(".")
                    id_post = url_post[index_slice+1:-1]
                    post["new_id"] = id_post

                    title = soup.find("div", {"class": "thread-title"})
                    if title != None:
                        post["title"] = title.get_text().strip()
                    else:
                        post["title"] = ''

                    article = soup.find_all("article", {"class": "content"})
                    if len(article) > 0:
                        list_content = article[0].find_all("span", {"class": "xf-body-paragraph"})
                        content = ""
                        for item in list_content:
                            content += item.get_text().strip()
                        post["content"] = content

                    div_tags = soup.find("div", {"class": "thread-tags"})
                    if div_tags != None:
                        list_tag = div_tags.find_all("a")
                        tags = []
                        for item in list_tag:
                            tag_content = item.get_text().strip()
                            tags.append(tag_content)
                        post["tags"] = tags

                    span_date = soup.find("span", {"class": "date"})
                    if span_date != None:
                        post["posting_date"] = span_date.span.get_text().strip()

                    created_at = int(datetime.timestamp(datetime.now()))
                    post["created_date"] = created_at

                    InsertNews(db, post)
                    
                    crawl_comment(url_post, id_post)
                    length_page += 1

                
            if length_page < config["LIMIT"]:
                return False
            else:
                return True
        else:
            return False

    except Exception as exc:
        # print("parse error:", exc)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tracklog.send(False, f"{config['DOMAIN']}__crawl.parse: {url_post}: {exc} - Line: {exc_tb.tb_lineno}")
        return False

                
def crawl_data(category_url, category_name):
    try:
        page = 0
        total_page = 0
        while page <= total_page:
            page += 1
            url = "%spage-%s" % (category_url, str(page))

            tracklog.send(True, f"{config['DOMAIN']}__Start Crawl: {url}")

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                if page == 1:
                    page_nav = soup.find("div", {"class": "PageNav"})
                    if page_nav != None:
                        total_page_str = page_nav.get("data-last")
                        if total_page_str.isdigit():
                            total_page = int(total_page_str)
                        else:
                            total_page = 0

                list_post = soup.find_all("a", {"class": "PreviewTooltip"})

                if not parse(list_post, category_name, total_page):
                    break

            time.sleep(config["SLEEP"])

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tracklog.send(False, f"{config['DOMAIN']}__crawl.crawl_data: {url}: {exc} - Line: {exc_tb.tb_lineno}")


def get_category(node):
    category = node.find("h3", {"class": "nodeTitle"})
    category_url = "%s%s" % (config["DOMAIN"], category.a["href"])
    category_name = category.a.string
    crawl_data(category_url, category_name)

def get_folder_category(folder_url):
    response = requests.get(folder_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        list_category = soup.find("ol", {"class": "nodeList uix_nodeStyle_0 section"})

        for category in list_category.contents:
            if str(category).strip() != "":
                check_node = category.div["class"]
                if "forumNodeInfo" in check_node:               
                    get_category(category)

def start_crawl():
    try:
        response = requests.get(config["FORUM"], headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            list_forum = soup.find("ol", {"id": "forums"})

            for forum in list_forum.contents:
                if str(forum).strip() != "":
                    if "category" in forum["class"]:
                        list_node = forum.find("ol", {"class": "nodeList"})
                        for node in list_node.contents:
                            if str(node).strip() != "":
                                check_node = node.div["class"]
                                if "categoryForumNodeInfo" in check_node:
                                    folder = node.find("h3", {"class": "nodeTitle"})
                                    folder_url = "%s%s" % (config["DOMAIN"], folder.a["href"])
                                    get_folder_category(folder_url)
                                elif "forumNodeInfo" in check_node:               
                                    get_category(node)

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tracklog.send(False, f"{config['DOMAIN']}crawl.start_crawl: {exc} - Line: {exc_tb.tb_lineno}")
    finally:
        tracklog.disconnect()