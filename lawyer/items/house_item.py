#!/usr/bin/python
#-*- coding: utf-8 -*-
import scrapy

class HourseItem(scrapy.Item):
    uuid=scrapy.Field()
    createtime = scrapy.Field()
    pid = scrapy.Field()
    #省
    province=scrapy.Field()
    #城市
    city=scrapy.Field()
    #区/县
    region=scrapy.Field()
    #街道
    street=scrapy.Field()
    #小区名称
    name=scrapy.Field()
    #楼层
    floor=scrapy.Field()
    #朝向
    orientation=scrapy.Field()
    #面积
    area=scrapy.Field()
    #价格
    toallPrice=scrapy.Field()
    #建筑时间
    years=scrapy.Field()
    #房产类型 二手房、商铺、写字楼
    type=scrapy.Field()
    #装修情况
    decoration=scrapy.Field()
    #容积率
    volume=scrapy.Field()

    #html
    html=scrapy.Field()
    #url
    url=scrapy.Field()
    # mongo集合 houses
    collection = scrapy.Field()
    #来源
    source = scrapy.Field()
