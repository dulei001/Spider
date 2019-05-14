#!/usr/bin/python
#-*- coding: utf-8 -*-
import re
import uuid
import scrapy
class alsSpider(scrapy.Spider):
    """阿拉善盟"""
    name = "als"
    provinceName=u"内蒙古"
    cityName=u"阿拉善盟"
    provinceCode="15"
    cityCode = "1501"
    level=u"地方法规"
    allowed_domains=["www.als.gov.cn"]


    start_urls = [
        'http://www.als.gov.cn',
        ]
    page_domain = "http://www.als.gov.cn%s"
    fagui_statr_arr=[
        {"name":u"命令", "url":"http://www.als.gov.cn/channels/83{0}.html","page":19},
        {"name": u"通知", "url": "http://www.als.gov.cn/channels/82{0}.html","page":14},
    ]

    def parse(self, response):
        for item in self.fagui_statr_arr:
             yield scrapy.Request(str(item["url"]).format(""), callback=self.parse_page_list, method='get',
                                 errback=self.handle_error, meta={'stype': item["name"]})
             for pages in range(2,int(item["page"]),1):
                  yield  scrapy.Request(str(item["url"]).format("_"+str(pages)), callback=self.parse_page_list, method='get',
                                                errback=self.handle_error,meta={'stype':item["name"]})

    def parse_page_list(self,response):
        for item in response.css(".ul1 li a"):
            detailbaseurl=  ''.join(item.css("::attr(href)").extract())
            if detailbaseurl.find('mp.weixin.qq.com')==-1:
                yield scrapy.Request(self.page_domain % detailbaseurl, callback=self.parse_detail, method='get',
                                     errback=self.handle_error, meta={'stype': response.meta["stype"]})

    def parse_detail(self,response):
        item = {}
        title = ''.join(response.css('h3::text').re('[^\s+]'))
        if  title!='':
           item['title'] = title
           item['anNo']=None
           item['pubish_time'] =re.search(r"(\d{4}-\d{1,2}-\d{1,2})",  ''.join(response.css(".source span:nth-child(1)::text").extract())).group(0)
           item['effect_time'] = None
           item['pubish_org'] = u'阿拉善盟行政公署'
           item['level']= self.level
           item['time_liness'] = u"现行有效"
           content =  ''.join(response.css('.contentbody').extract())
           item["content"] =re.sub('((class|style|color|href|target|align|title)="[^"]*?")|(<img .*?>)', '', content)  # 内容'''
           item['url'] = response.url
           item["provinceName"]=self.provinceName
           item["cityName"]=self.cityName
           item["provinceCode"] = self.provinceCode
           item["cityCode"] = self.cityCode
           item['sIndex'] = None
           item["sTypeName"]=response.meta["stype"]
           item['source'] = u"阿拉善盟行政公署"
           # 是否导入正式数据库
           item['export'] = '0'
           item['collection'] = 'fagui'
           item["Id"]=str(uuid.uuid1()).replace('-', '')
           return  item



    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)


