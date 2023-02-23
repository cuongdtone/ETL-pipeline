# -*- coding: utf-8 -*-
# @Organization  : TMT
# @Author        : Cuong Tran
# @Time          : 2/23/2023

import os
import yaml
from pymongo import MongoClient


MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB = os.getenv('MONGO_DB')
MONGO_COLLECTION = 'diaries'

DOMAIN = os.getenv('DOMAIN')


class DiaryHandler:
    def __init__(self):
        client = MongoClient(MONGO_URI)
        self.db = client[MONGO_DB]

    def read(self):
        try:
            collection = self.db[MONGO_COLLECTION]
            find_result = collection.find({"domain": DOMAIN, "bookmark": "S"}, limit=1)
            if find_result.count() != 0:
                find_result = find_result[0]
                print(find_result)
                collection.update_one({
                    '_id': find_result['_id']
                }, {
                    '$set': {
                        'bookmark': 'N'
                    }
                }, upsert=False)
                return find_result

            return {}
        except Exception as exc:
            print(exc)
            return {}

    def write(self, item: dict):
        try:
            if '_id' in item.keys():
                del item['_id']
            collection = self.db[MONGO_COLLECTION]
            item.update({'domain': DOMAIN, "bookmark": "S"})
            return collection.insert_one(item)
        except Exception as exc:
            print(exc)

    def update(self, item: dict):
        try:
            collection = self.db[MONGO_COLLECTION]
            collection.update_one({'_id': item['_id']},
                                  {'$set': item}
                                  )
        except Exception as exc:
            print(exc)
