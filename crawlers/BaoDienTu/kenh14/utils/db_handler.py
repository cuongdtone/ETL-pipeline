# -*- coding: utf-8 -*-
# @Organization  : TMT
# @Author        : Cuong Tran
# @Time          : 2/13/2023


import os
import yaml
from pymongo import MongoClient


MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB = os.getenv('MONGO_DB')
DOMAIN = os.getenv('DOMAIN')

print('MONGO: ', MONGO_URI, MONGO_DB)

def ConnectDB():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    return db


def InsertNews(db, item):
    try:
        if db is None:
            db = ConnectDB()
        collection = db["news"]
        find_result = collection.find({"domain": DOMAIN, "new_id": item["new_id"]}, limit=1)
        # print(find_result.count())
        print(item)
        if find_result.count() != 0:
            # Update item
            # print('Update')
            collection.update_one({
                '_id': find_result[0]['_id']
            }, {
                '$set': item
            }, upsert=False)
        else:
            # Insert item
            # print('Inserted')
            collection.insert_one(item)
    except Exception as exc:
        print(exc)
        pass
