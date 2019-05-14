#!/usr/bin/python
#-*- coding: utf-8 -*-
import json
import re
import uuid
import scrapy
class zcjdSpider(scrapy.Spider):
    """中华人民共和国司法部"""
    name = "zcjd"
    provinceName=None
    cityName=None
    provinceCode=None
    cityCode = None
    level=u"政策解读"
    start_urls = [
        'http://www.moj.gov.cn/json/596_1.json',
        ]
    page_domain = "http://www.moj.gov.cn%s"
    def parse(self, response):
        data = json.loads(response.body_as_unicode())
        for item in data:
            yield scrapy.Request(url=self.page_domain % item['infostaticurl'],callback=self.parse_detail, method='get',errback=self.handle_error,)


    def parse_detail(self,response):
        item = {}
        title = ''.join(response.css('.con_bt::text').re('[^\s+]'))
        if  title!='':
           item['title'] = title
           item['anNo']=''
           item['pubish_time'] = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", ''.join(response.css('.con_time span:nth-child(1)::text').re('[^\s+]'))).group(0)
           item['effect_time'] =None
           item['pubish_org'] = ''.join(response.css('.con_time span:nth-child(2)::text').re('[^\s+]'))
           item['level']= self.level
           item['time_liness'] = u"现行有效"
           content =  ''.join(response.xpath('//div[@id="content"]/span').extract())
           item["content"] =re.sub('((id|class|style|color|href|target|align|title)="[^"]*?")|(<img .*?>)', '', content)  # 内容'''
           item['url'] = response.url
           item["provinceName"]=self.provinceName
           item["cityName"]=self.cityName
           item["provinceCode"] = self.provinceCode
           item["cityCode"] = self.cityCode
           item['sIndex'] = None
           item["sTypeName"]=None
           item['source'] = u"共和国司法部"
           # 是否导入正式数据库
           item['export'] = '0'
           item['collection'] = 'fagui'
           item["Id"]=str(uuid.uuid1()).replace('-', '')
           return  item



    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)


