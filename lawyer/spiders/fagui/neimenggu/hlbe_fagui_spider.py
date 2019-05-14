#!/usr/bin/python
#-*- coding: utf-8 -*-
import re
import uuid
import json
import scrapy

class HLBESpider(scrapy.Spider):
    # 呼伦贝尔市人民政府

    name = "hlbe"
    provinceName = u"内蒙古"
    cityName = u"呼伦贝尔市"
    provinceCode='15'
    cityCode='1507'
    level = u"地方法规"
    pubish_time='2019-04-24'

    allowed_domains=["www.hlbe.gov.cn"]

    start_urls = [ 'http://www.hlbe.gov.cn/']

    fgparamlist = [
        {'type': u'决定', 'page': '1', 'url':'http://www.hlbe.gov.cn/opennessTarget/?branch_id=541790c49a05c24b2a17f662&column_code=&topic_id=52c6626ce1b1d180587d0ef0&page=%d'},
        {'type': u'通知', 'page': '38', 'url': 'http://www.hlbe.gov.cn/opennessTarget/?branch_id=541790c49a05c24b2a17f662&column_code=&topic_id=52c662abe1b1d18058b04f2f&page=%d'},
        {'type': u'意见', 'page': '5', 'url': 'http://www.hlbe.gov.cn/opennessTarget/?branch_id=541790c49a05c24b2a17f662&column_code=&topic_id=52c662ece1b1d1cb5ec490f7&page=%d'},
        {'type': u'其他', 'page': '10', 'url': 'http://www.hlbe.gov.cn/opennessTarget/?branch_id=541790c49a05c24b2a17f662&column_code=&topic_id=53fc44d69a05c23d572ca332&page=%d'}
    ]

    page_domain = "http://www.hlbe.gov.cn%s"

    def parse(self, response):
        send_requests = []

        for item in self.fgparamlist:
            page = int(item['page'])
            listurl = item['url']
            for index in range(1, page + 1):
                newurl = listurl % index
                send_requests.append(scrapy.Request(newurl, callback=self.parse_list, method='get', errback=self.handle_error,meta={'type': item['type']}, ))

        return send_requests


    def parse_list(self, response):
        for item in response.css(".tboxs table td a"):
            detail_url =  self.page_domain % ''.join(item.css("::attr(href)").extract()).replace('../..','')
            yield scrapy.Request(detail_url, callback=self.parse_detail, method='get',errback=self.handle_error,meta={'type': response.meta['type']})
        pass


    def parse_detail(self,response):
        item = {}
        title = ''.join(response.css('#artibodyTitle::text').re('[^\s+]'))
        if title != '':
            item['title'] = title
            anNo = ''.join(response.css('.is-xxgkinfo tr:nth-child(4) td:nth-child(2)::text').extract())
            if anNo == '':
                anNo = None
            item['anNo'] = anNo
            item['pubish_time'] = ''.join(response.css('.is-xxgkinfo tr:nth-child(5) td:nth-child(2)::text').extract())
            item['effect_time'] = None
            item['pubish_org'] = ''.join(response.css('.is-xxgkinfo tr:nth-child(2) td:nth-child(2)::text').extract())
            item['level'] = self.level
            item['time_liness'] = u"现行有效"
            content = ''.join(response.css('.is-newscontnet').extract())
            item["content"] = re.sub('((class|style|color|href|target|align|title)="[^"]*?")|(<img .*?>)', '',content)  # 内容'''
            #item["content"] = ''
            item['url'] = response.url
            item["provinceName"] = self.provinceName
            item["cityName"] = self.cityName
            item["provinceCode"] = self.provinceCode
            item["cityCode"] = self.cityCode
            item['sIndex'] = ''.join(response.css('.is-xxgkinfo tr:nth-child(1) td:nth-child(2)::text').extract())
            item["sTypeName"] = response.meta["type"]
            item['source'] = u"呼伦贝尔市人民政府"
            # 是否导入正式数据库
            item['export'] = '0'
            item['collection'] = 'fagui'
            item["Id"] = str(uuid.uuid1()).replace('-', '')
            return item

    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)