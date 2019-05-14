#!/usr/bin/python
#-*- coding: utf-8 -*-
import os
import uuid
from datetime import datetime
import pymongo


class MongoPipeline(object):

    def __init__(self, mongo_uri, mongo_db,mongo_replicat_set,mongo_username,mongo_password):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_replicat_set = mongo_replicat_set
        self.mongo_username = mongo_username
        self.mongo_password = mongo_password

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'spider'),
            mongo_replicat_set = crawler.settings.get('MONGO_REPLICAT_SET'),
            mongo_username=crawler.settings.get('MONGO_USERNAME'),
            mongo_password=crawler.settings.get('MONGO_PASSWORD'),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri,replicaSet=self.mongo_replicat_set)
        self.client[self.mongo_db].authenticate(self.mongo_username, self.mongo_password)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # if item.has_key("uuid")==False:
        #     item["uuid"]=str(uuid.uuid1())

        # item['createtime'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # item['pid']=os.getpid()
        if dict(item).has_key('collection'):
            model = dict(item)
            del model['collection']
            self.db[item["collection"]].insert(model)
        else:
            self.db[spider.name].insert(dict(item))
        return item