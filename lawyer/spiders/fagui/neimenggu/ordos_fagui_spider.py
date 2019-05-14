#!/usr/bin/python
#-*- coding: utf-8 -*-
import re
import uuid
import json
import scrapy
from  dal.service.StatuteData import StatuteData

class OrdosSpider(scrapy.Spider):
    #  鄂尔多斯市人民政府网

    name = "ordos"
    statuteData = StatuteData()

    provinceName = u"内蒙古"
    cityName = u"鄂尔多斯"
    provinceCode='15'
    cityCode='1505'
    level = u"地方法规"
    pubish_time='2019-04-23'

    allowed_domains=["ordos.gov.cn"]

    start_urls = [ 'http://xxgk.ordos.gov.cn/xxgk/channel/ordos_xxw/col10204f.html']

    page_domain = "http://xxgk.ordos.gov.cn%s"

    def parse(self, response):
        send_requests = []
        pageSize=15;

        for item in response.css('#tree4 div'):
            url=''.join(item.css("a::attr(href)").extract()).replace('../..','')
            type=''.join(item.css("a::text").extract()).replace(' ','')
            dcount=''.join(item.css("font::text").extract()).replace(' ','')
            dcount= re.findall("\d+",dcount)[0]
            page= (int(dcount) + pageSize - 1) / pageSize;

            for index in range(1, page + 1):
                if index==1:
                    send_requests.append(scrapy.Request(self.page_domain % url, callback=self.parse_list, method='get', errback=self.handle_error,meta={'type':type}, ))
                else:
                    newurl=''.join((url, '&pos=%d' % index ))
                    send_requests.append(scrapy.Request(self.page_domain % newurl, callback=self.parse_list, method='get', errback=self.handle_error,meta={'type': type }, ))

        return send_requests



    def parse_list(self, response):
        for item in response.css(".recordlist a"):
            detail_url =  self.page_domain % ''.join(item.css("::attr(href)").extract()).replace('../..','')
            yield scrapy.Request(detail_url, callback=self.parse_detail, method='get',errback=self.handle_error,meta={'type': response.meta['type']})
        pass

    def parse_detail(self, response):
        item = {}
        title = ''.join(response.css('#title::text').extract_first())
        if title != '':
            item['title'] = title
            item['anNo'] = ''.join(response.css('.detail table tr:nth-child(4) td:nth-child(2)::text').extract())
            item['pubish_time'] =''.join(response.css('.detail table tr:nth-child(4) td:nth-child(4)::text').extract())
            item['effect_time'] = None
            item['pubish_org'] = ''.join(response.css('.detail table tr:nth-child(2) td:nth-child(2)::text').extract())
            item['level'] = self.level
            item['time_liness'] = u"现行有效"
            content = ''.join(response.css('#content').extract())
            item["content"] = re.sub('((class|style|color|href|target|align|title)="[^"]*?")|(<img .*?>)', '',content)  # 内容'''
            #item["content"] = ''
            item['url'] = response.url
            item["provinceName"] = self.provinceName
            item["cityName"] = self.cityName
            item["provinceCode"] = self.provinceCode
            item["cityCode"] = self.cityCode
            item['sIndex'] = ''.join(response.css('.detail table tr:nth-child(1) td:nth-child(2)::text').extract())
            item["sTypeName"] = response.meta["type"]
            item['source'] = u"鄂尔多斯市人民政府"
            # 是否导入正式数据库
            item['export'] = '0'
            item['collection'] = 'fagui'
            item["Id"] = str(uuid.uuid1()).replace('-', '')
            return item


    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)