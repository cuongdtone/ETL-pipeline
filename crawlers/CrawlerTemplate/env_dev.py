# -*- coding: utf-8 -*-
# @Organization  : TMT
# @Author        : Cuong Tran
# @Time          : 2/13/2023

import os


def set_dev_env():
    os.environ['DATA_LAKE'] = 'mongo'
    os.environ['KAFKA_BOOTSTRAP_SERVER'] = '192.168.1.161:9092'
    os.environ['KAFKA_TOPIC'] = 'news'
    os.environ['MONGO_URI'] = '192.168.1.159:27017'
    os.environ['MONGO_DB'] = 'CrawlerDataDB'
    os.environ['DOMAIN'] = 'https://kenh14.vn/'


