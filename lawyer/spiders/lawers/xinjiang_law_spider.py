#!/usr/bin/python
# -*- coding: utf-8 -*-
import scrapy
from lawyer.items.LawyerInfo_item import  LawyerInfoItem
from scrapy.spiders import Spider
class XinJiang_LawyerSpider(Spider):
    name = "xinjiang_law_spider"
   # allowed_domains = ['oa.xjlx.org']
    start_urls = [
        "http://oa.xjlx.org/html/lscx1.asp" #新疆律师
    ]

    # 爬虫入口
    def parse(self, response):
        baseurl = "http://oa.xjlx.org/html/lscx1.asp?page={0}"
        for i in range(1, 464):
             yield scrapy.Request(url=baseurl.format(str(i)), method="GET",callback=self.parse_detail,errback=self.handle_error)


    #律师信息
    def parse_detail(self,response):
        for x in response.xpath(u'//td[text()="序号"]/ancestor::table[1]/tr[position()>1]'):
            item = LawyerInfoItem()
            name = ''.join(x.xpath('td[2]/text()').re('[^\s+]'))
            if name != '':
                item['name'] = name
                item['sex'] = ''
                item['personnel_type'] = ''
                item['firm'] = ''
                item['lawnumber'] = ''.join(x.xpath('td[3]/text()').re('[^\s+]'))
                item['get_time'] = ''
                item['start_time'] = ''
                item['province']=u'新疆'
                item['education'] = ''
                item['cert_type'] = ''
                item['headurl'] = ''
                item['ispartnership'] = ''
                item['nation'] = ''
                item['political_status'] = ''
                item['professional_status'] = ''
                item['profession'] = ''
                item['url'] = response.url
                item['collection'] = 'lawyers'
                yield item

    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)





