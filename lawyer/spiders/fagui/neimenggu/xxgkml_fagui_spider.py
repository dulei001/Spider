#!/usr/bin/python
#-*- coding: utf-8 -*-
import re
import uuid
import scrapy
from  dal.service.StatuteData import StatuteData
class xxgkmlSpider(scrapy.Spider):
    """锡林郭勒盟"""

    name = "xxgkmlfagui"
    provinceName=u"内蒙古"
    cityName=u"锡林郭勒盟"
    provinceCode="15"
    cityCode = "1511"
    level=u"地方法规"
    allowed_domains=["xxgk.xlgl.gov.cn"]


    start_urls = [
        'http://xxgk.xlgl.gov.cn',
        ]
    page_domain = "http://xxgk.xlgl.gov.cn/xsbgt/xxgkml%s"
    fagui_statr_arr=[
        {"name":u"决定", "url":"http://xxgk.xlgl.gov.cn/xsbgt/xxgkml/1638/1640/index_17889{0}.html","page":1},
        {"name": u"命令", "url": "http://xxgk.xlgl.gov.cn/xsbgt/xxgkml/1638/1641/index_17889{0}.html","page":1},
        {"name": u"公报", "url": "http://xxgk.xlgl.gov.cn/xsbgt/xxgkml/1638/1642/index_17889{0}.html","page":1},
        {"name": u"公告", "url": "http://xxgk.xlgl.gov.cn/xsbgt/xxgkml/1638/1643/index_17889{0}.html","page":39},
        {"name": u"通告", "url": "http://xxgk.xlgl.gov.cn/xsbgt/xxgkml/1638/1644/index_17889{0}.html","page":2},
        {"name": u"意见", "url": "http://xxgk.xlgl.gov.cn/xsbgt/xxgkml/1638/1645/index_17889{0}.html","page":2},
        {"name": u"通知", "url": "http://xxgk.xlgl.gov.cn/xsbgt/xxgkml/1638/1646/index_17889{0}.html","page":30},
        {"name": u"通报", "url": "http://xxgk.xlgl.gov.cn/xsbgt/xxgkml/1638/1647/index_17889{0}.html","page":1},
        {"name": u"报告", "url": "http://xxgk.xlgl.gov.cn/xsbgt/xxgkml/1638/1648/index_17889{0}.html","page":8},
        {"name": u"批复", "url": "http://xxgk.xlgl.gov.cn/xsbgt/xxgkml/1638/1650/index_17889{0}.html","page":1},
        {"name": u"议案", "url": "http://xxgk.xlgl.gov.cn/xsbgt/xxgkml/1638/1651/index_17889{0}.html","page":1},
        {"name": u"函", "url": "http://xxgk.xlgl.gov.cn/xsbgt/xxgkml/1638/1652/index_17889{0}.html","page":1},
        {"name": u"其他", "url": "http://xxgk.xlgl.gov.cn/xsbgt/xxgkml/1638/1654/index_17889{0}.html","page":100},
    ]

    def parse(self, response):
        for item in self.fagui_statr_arr:
             yield scrapy.Request(str(item["url"]).format(""), callback=self.parse_page_list, method='get',
                                 errback=self.handle_error, meta={'stype': item["name"]})
             for pages in range(1,int(item["page"]),1):
                  yield  scrapy.Request(str(item["url"]).format("_"+str(pages)), callback=self.parse_page_list, method='get',
                                                errback=self.handle_error,meta={'stype':item["name"]})

    def parse_page_list(self,response):
        for item in response.css("td a"):
            detailbaseurl=  self.page_domain % ''.join(item.css("::attr(href)").extract()).replace('../..','')
            yield scrapy.Request(detailbaseurl, callback=self.parse_detail, method='get',
                                 errback=self.handle_error, meta={'stype': response.meta["stype"]})

    def parse_detail(self,response):
        item = {}
        title = ''.join(response.css('.title span:nth-child(2)::text').extract())
        if  title!='':
           item['title'] = title
           item['anNo']=''.join(response.css('.docNo span:nth-child(2)::text').extract())
           item['pubish_time'] = ''.join(response.xpath('//div[@class="idxid"][last()]/span[2]/text()').extract())
           item['effect_time'] = None
           item['pubish_org'] = ''.join(response.css('.organ span:nth-child(2)::text').extract())
           item['level']= self.level
           item['time_liness'] = u"现行有效"
           content =  ''.join(response.css('.xx_content').extract())
           item["content"] =re.sub('((class|style|color|href|target|align|title)="[^"]*?")|(<img .*?>)', '', content)  # 内容'''
           item['url'] = response.url
           item["provinceName"]=self.provinceName
           item["cityName"]=self.cityName
           item["provinceCode"] = self.provinceCode
           item["citCode"] = self.cityCode
           item['sIndex'] = ''.join(response.css('.idxid span:nth-child(2)::text').extract())
           item["sTypeName"]=response.meta["stype"]
           item['source'] = u"锡林郭勒盟"
           # 是否导入正式数据库
           item['export'] = '0'
           item['collection'] = 'fagui'
           item["Id"]=str(uuid.uuid1()).replace('-', '')
           return  item



    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)


