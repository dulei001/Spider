#!/usr/bin/python
#-*- coding: utf-8 -*-
import scrapy


class ContractItem(scrapy.Item):
    one_level_title = scrapy.Field()
    two_level_title = scrapy.Field()
    title=scrapy.Field()
    content=scrapy.Field()
    url=scrapy.Field()
    create_time=scrapy.Field()

