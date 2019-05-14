#!/usr/bin/python
#-*- coding: utf-8 -*-
import scrapy


class ArticleItem(scrapy.Item):
    title=scrapy.Field()
    pass
