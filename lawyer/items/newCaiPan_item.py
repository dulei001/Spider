#!/usr/bin/python
#-*- coding: utf-8 -*-
import scrapy

#新的裁判文书模型
class NewCaiPanItem(scrapy.Item):
    item = {}
    # 标题
    title = scrapy.Field()
    # 法院
    fanyuan = scrapy.Field()
    # 案号
    anhao = scrapy.Field()
     # 案由
    anyou = scrapy.Field()
       # 案件类型
    type = scrapy.Field()
    # 文书类型
    doctype = scrapy.Field()
    #审理程序
    shenliApp=scrapy.Field()
    # 发布时间
    stime = scrapy.Field()
    # 内容
    content = scrapy.Field()
    #采集来源
    source = scrapy.Field()
    #url
    url = scrapy.Field()
    #采集时间
    createtime =  scrapy.Field()


    # mongo集合 houses
    collection = scrapy.Field()



