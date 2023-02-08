import yaml
from pymongo import MongoClient

config = yaml.load(open('settings.yaml', 'r'), Loader=yaml.FullLoader)
DOMAIN = config['DOMAIN']


def ConnectDB():
    client = MongoClient(config["MONGO_URI"])
    db = client[config["MONGO_DB"]]
    return db


def InsertNews(db, item):
    try:
        if db is None:
            db = ConnectDB()

        collection = db["news"]

        find_result = collection.find({"domain": config['DOMAIN'], "new_id": item["new_id"]}, limit=1)
        if find_result.count() != 0:
            # Update item
            collection.update_one({
                '_id': find_result[0]['_id']
            }, {
                '$set': item
            }, upsert=False)
        else:
            # Insert item
            collection.insert_one(item)
    except Exception as exc:
        pass
