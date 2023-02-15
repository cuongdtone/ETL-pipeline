# -*- coding: utf-8 -*-
# @Organization  : TMT
# @Author        : Cuong Tran
# @Time          : 2/13/2023

import os


def set_dev_env():
    os.environ['KAFKA_BOOTSTRAP_SERVER'] = 'localhost:9092'
    os.environ['KAFKA_TOPIC'] = 'news'
    os.environ['DOMAIN'] = 'https://kenh14.vn/'

    