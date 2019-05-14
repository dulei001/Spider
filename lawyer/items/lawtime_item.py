#!/usr/bin/python
#-*- coding: utf-8 -*-
import scrapy


class ArticleItem(scrapy.Item):
    title=scrapy.Field()
    content=scrapy.Field()
    organization=scrapy.Field()
    source=scrapy.Field()
    publish_time=scrapy.Field()
    release_time=scrapy.Field()
    level=scrapy.Field()
    effect=scrapy.Field()

