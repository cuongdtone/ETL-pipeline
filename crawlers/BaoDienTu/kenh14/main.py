# -*- coding: utf-8 -*-
# @Organization  : TMT
# @Author        : Cuong Tran
# @Time          : 2/13/2023
import os
from datetime import datetime, timedelta

from utils import env_dev
from utils.diary import DiaryHandler
import crawl

if __name__ == "__main__":
    diary = DiaryHandler()
    setting = diary.read()
    setting.update({'mode': os.getenv('ARG1')})

    # ---------------- Diary process --------------#
    if setting['mode'] == 'old':
        if 'recent_date' in setting.keys() and 'end_date' in setting.keys():
            setting['recent_date'] = setting['end_date']
            end_date = datetime.strptime(setting['end_date'], '%d/%m/%Y').date()
            end_date = end_date - timedelta(days=1)
            setting['end_date'] = end_date.strftime('%d/%m/%Y')
        else:
            setting['recent_date'] = datetime.today().strftime('%d/%m/%Y')
            end_date = datetime.today() - timedelta(days=1)
            setting['end_date'] = end_date.strftime('%d/%m/%Y')
            setting['recent_page'] = 1

    setting['recent_page'] = int(setting['recent_page']) + 15
    _id = diary.write(setting)
    setting.update({'_id': _id.inserted_id})

    # ---------------- Run crawler --------------#
    end_page = crawl.start_crawl(**setting)

    # ---------------- Update diary --------------#
    setting['recent_page'] = end_page
    diary.update(setting)
