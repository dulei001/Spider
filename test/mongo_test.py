#!/usr/bin/python
#-*- coding: utf-8 -*-
import uuid
from pymongo import MongoClient


def main():
    # 两地址
    CONN_ADDR1 = 'dds-m5ee1e049673a1541.mongodb.rds.aliyuncs.com:3717'
    CONN_ADDR2 = 'dds-m5ee1e049673a1542.mongodb.rds.aliyuncs.com:3717'
    REPLICAT_SET = 'mgset-2808337'
    username = 'lvhe'
    password = 'lvhe1q2w3e4r'
    # 获取mongoclient
    client = MongoClient([CONN_ADDR1, CONN_ADDR2], replicaSet=REPLICAT_SET)
    # 授权. 这里的user基于admin数据库授权
    client.spider.authenticate(username, password)
    # 使用test数据库的collection:testColl做例子, 插入doc, 然后根据DEMO名查找
    demo_name = 'python-' + str(uuid.uuid1())
    print 'demo_name:', demo_name
    doc = dict(DEMO=demo_name, MESG="Hello ApsaraDB For MongoDB")
    doc_id = client.spider.house.insert(doc)
    print 'doc_id:', doc_id
    for d in client.spider.testColl.find(dict(DEMO=demo_name)):
        print 'find documents:', d

if __name__ == '__main__':
    main()