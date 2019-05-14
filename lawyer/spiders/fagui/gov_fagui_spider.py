#!/usr/bin/python
#-*- coding: utf-8 -*-
import re
import uuid
import scrapy
class govSpider(scrapy.Spider):
    """国务院"""
    name = "gov"
    provinceName=None
    cityName=None
    provinceCode=None
    cityCode = None
    level=u"行政法规"
    start_urls = [
        'http://www.gov.cn',
        ]
    fagui_statr_arr=[
        { "url":"http://sousuo.gov.cn/list.htm?q=&n=15&p={0}&t=paper&sort=pubtime&childtype=&subchildtype=&pcodeJiguan=&pcodeYear=&pcodeNum=&location=&searchfield=&title=&content=&pcode=&puborg=&timetype=timeqb&mintime=&maxtime=","page":357},
    ]

    def parse(self, response):
        for item in self.fagui_statr_arr:
             for pages in range(0,int(item["page"]),1):
                  yield  scrapy.Request(str(item["url"]).format(str(pages)), callback=self.parse_page_list, method='get', dont_filter=True,
                                                errback=self.handle_error)

    def parse_page_list(self,response):
        for item in response.xpath("//table[@class='dataList']/tr[position()>1]"):
            detailbaseurl=  ''.join(item.css("td a::attr(href)").extract())
            title = ''.join(item.css('td a::text').re('[^\s+]'))
            anNo = ''.join(item.css('td:nth-child(3)::text').re('[^\s+]'))
            pubish_time =''.join(item.css('td:nth-child(4)::text').extract()).replace(u"年", "-").replace(u"月", "-").replace(u"日", "")
            effect_time = ''.join(item.css('td:nth-child(5)::text').extract()).replace(u"年", "-").replace(u"月", "-").replace(u"日", "")
            pubish_org=''.join(item.css('td:nth-child(2) ul li:nth-child(3)::text').re('[^\s+]'))
            yield scrapy.Request(detailbaseurl,
                                 callback=self.parse_detail,
                                 method='get' ,
                                 dont_filter=True,
                                 meta={
                                     'anNo':anNo,
                                     'title':title,
                                     'effect_time':effect_time,
                                     'pubish_time':pubish_time,
                                     'pubish_org':pubish_org
                                 },
                                 errback=self.handle_error
                                 )

    def parse_detail(self,response):
        item = {}
        title = response.meta['title']
        if  title!='':
           item['title'] = title
           item['anNo']=response.meta['anNo']
           item['pubish_time'] =response.meta['pubish_time']
           item['effect_time'] =response.meta['effect_time']
           item['pubish_org'] = response.meta['pubish_org']
           item['level']= self.level
           item['time_liness'] = u"现行有效"
           content =  ''.join(response.xpath('//td[@class="b12c"]/*').extract())
           item["content"] =re.sub('((id|class|style|color|href|target|align|title)="[^"]*?")|(<img .*?>)', '', content)  # 内容'''
           item['url'] = response.url
           item["provinceName"]=self.provinceName
           item["cityName"]=self.cityName
           item["provinceCode"] = self.provinceCode
           item["cityCode"] = self.cityCode
           item['sIndex'] = None
           item["sTypeName"]=None
           item['source'] = u"中央人民政府"
           # 是否导入正式数据库
           item['export'] = '0'
           item['collection'] = 'fagui'
           item["Id"]=str(uuid.uuid1()).replace('-', '')
           return  item



    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)


