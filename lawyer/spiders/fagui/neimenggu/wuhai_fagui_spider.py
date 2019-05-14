#!/usr/bin/python
#-*- coding: utf-8 -*-
import re
import uuid
import scrapy
class wuhaiSpider(scrapy.Spider):
    """乌海市"""

    name = "wuhai"
    provinceName=u"内蒙古"
    cityName=u"乌海市"
    provinceCode="15"
    cityCode = "1509"
    level=u"地方法规"
    start_urls = [
        'http://jxw.wuhai.gov.cn',
        ]
    page_domain = "http://jxw.wuhai.gov.cn%s"
    fagui_statr_arr=[
        {"name":u"公告", "url":"http://jxw.wuhai.gov.cn/jxw/250901/250908/e5c5000f-{0}.html","page":39},
    ]

    def parse(self, response):
        for item in self.fagui_statr_arr:
             for pages in range(1,int(item["page"]),1):
                  yield  scrapy.Request(str(item["url"]).format(str(pages)), callback=self.parse_page_list, method='get',
                                                errback=self.handle_error,meta={'stype':item["name"]})

    def parse_page_list(self,response):
        for item in response.css(".xxgkml_list li a"):
            detailbaseurl=  self.page_domain % ''.join(item.css("::attr(href)").extract())
            yield scrapy.Request(detailbaseurl, callback=self.parse_detail, method='get',
                                 errback=self.handle_error, meta={'stype': response.meta["stype"]})

    def parse_detail(self,response):
        item = {}
        title = ''.join(response.css('.wh_xl_t::text').re('[^\s+]'))
        print title
        if  title!='':
           item['title'] = title
           item['anNo']=''.join(response.xpath('//*[@id="5df97e575519436bb6cb417deb2d0d1a"]/div[2]/div[1]/div[2]/div[1]/li[2]/span[2]/text').re('[^\s+]'))
           item['pubish_time'] =''.join(response.xpath('//*[@id="5df97e575519436bb6cb417deb2d0d1a"]/div[2]/div[1]/div[2]/div[1]/li[2]/span[4]/text()').extract()).replace(u"年","-").replace(u"月","-").replace(u"日","")
           item['effect_time'] = None
           item['pubish_org'] = u'乌海市人民政府'
           item['level']= self.level
           item['time_liness'] = u"现行有效"
           content =  ''.join(response.css('#wh_x_c').extract())
           item["content"] =re.sub('((id|class|style|color|href|target|align|title)="[^"]*?")|(<img .*?>)', '', content)  # 内容'''
           item['url'] = response.url
           item["provinceName"]=self.provinceName
           item["cityName"]=self.cityName
           item["provinceCode"] = self.provinceCode
           item["cityCode"] = self.cityCode
           item['sIndex'] = ''.join(response.xpath('//*[@id="5df97e575519436bb6cb417deb2d0d1a"]/div[2]/div[1]/div[2]/div[1]/li[1]/span[2]/text()').extract())
           item["sTypeName"]=response.meta["stype"]
           item['source'] = u"乌海市人民政府"
           # 是否导入正式数据库
           item['export'] = '0'
           item['collection'] = 'fagui'
           item["Id"]=str(uuid.uuid1()).replace('-', '')
           return  item



    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)


