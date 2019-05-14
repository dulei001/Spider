#!/usr/bin/python
#-*- coding: utf-8 -*-
import scrapy


class LawyerInfoItem(scrapy.Item):
    uuid = scrapy.Field()
    createtime = scrapy.Field()
    pid = scrapy.Field()
    #姓名
    name=scrapy.Field()
    #性别0-男 1-女
    sex=scrapy.Field()
    #民族
    nation=scrapy.Field()
    #学历
    education=scrapy.Field()
    #政治面貌
    political_status=scrapy.Field()
    #头像路径
    headurl=scrapy.Field()
    #律师职业证号
    lawnumber=scrapy.Field()
    #职业状态:0-正常、1-注销
    professional_status=scrapy.Field()
    #人员类型:专职
    personnel_type=scrapy.Field()
    #首次执业时间
    start_time=scrapy.Field()
    #资格证获取时间
    get_time=scrapy.Field()
    #证书类型
    cert_type=scrapy.Field()
    #专业(擅长领域)
    profession=scrapy.Field()
    #是否合伙人 0-否 1-是
    ispartnership=scrapy.Field()
    #所属律所
    firm=scrapy.Field()
    #省份 比如是北京
    province=scrapy.Field()
    #url
    url=scrapy.Field()
    # mongo集合 houses
    collection = scrapy.Field()



