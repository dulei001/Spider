#!/usr/bin/python
#-*- coding: utf-8 -*-
import scrapy


class ArticleItem(scrapy.Item):
    # 内容标题
    one_level = scrapy.Field()
    two_level = scrapy.Field()
    url=scrapy.Field()
    #概念
    concept=scrapy.Field()
    #构成要件
    structure=scrapy.Field()
    #认定
    maintain=scrapy.Field()
    #量刑标准
    measurement_standard=scrapy.Field()
    #立案标准
    register_standard=scrapy.Field()
    #司法解释
    judicial_interpretation=scrapy.Field()
    #辩护词
    defence_word=scrapy.Field()
    #案例
    case=scrapy.Field()
    create_time=scrapy.Field()
