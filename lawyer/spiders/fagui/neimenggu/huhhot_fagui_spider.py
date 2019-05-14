#!/usr/bin/python
#-*- coding: utf-8 -*-
import re
import uuid
import json
import scrapy
from  dal.service.StatuteData import StatuteData

class HuhhotSpider(scrapy.Spider):
    # 呼和浩特市人民政府

    name = "huhhot"
    statuteData = StatuteData()

    provinceName = u"内蒙古"
    cityName = u"呼和浩特"
    provinceCode='15'
    cityCode='1506'
    level = u"地方法规"
    pubish_time='2019-04-23'

    allowed_domains=["www.huhhot.gov.cn"]

    start_urls = [ 'http://www.huhhot.gov.cn/zwgk/zfxxgkzl/zfxxgkmlx/']

    fgparamlist = [
        {'type': u'决定', 'page': '3', 'url':'http://www.huhhot.gov.cn/zwgk/zfxxgkzl/zfxxgkmlx/218/219/index_74%s.html'},
        {'type': u'命令', 'page': '1', 'url': 'http://www.huhhot.gov.cn/zwgk/zfxxgkzl/zfxxgkmlx/218/220/index_74%s.html'},
        {'type': u'通告', 'page': '4', 'url': 'http://www.huhhot.gov.cn/zwgk/zfxxgkzl/zfxxgkmlx/218/221/index_74%s.html'},
        {'type': u'公告', 'page': '6', 'url': 'http://www.huhhot.gov.cn/zwgk/zfxxgkzl/zfxxgkmlx/218/1888/index_74%s.html'},
        {'type': u'意见', 'page': '6', 'url': 'http://www.huhhot.gov.cn/zwgk/zfxxgkzl/zfxxgkmlx/218/222/index_74%s.html'},
        {'type': u'通知', 'page': '67', 'url': 'http://www.huhhot.gov.cn/zwgk/zfxxgkzl/zfxxgkmlx/218/223/index_74%s.html'},
        {'type': u'通报', 'page': '2', 'url': 'http://www.huhhot.gov.cn/zwgk/zfxxgkzl/zfxxgkmlx/218/224/index_74%s.html'},
        {'type': u'批复', 'page': '30', 'url': 'http://www.huhhot.gov.cn/zwgk/zfxxgkzl/zfxxgkmlx/218/225/index_74%s.html'},
        {'type': u'报告', 'page': '10', 'url': 'http://www.huhhot.gov.cn/zwgk/zfxxgkzl/zfxxgkmlx/218/1020/index_74%s.html'},
        {'type': u'会议纪要', 'page': '3', 'url': 'http://www.huhhot.gov.cn/zwgk/zfxxgkzl/zfxxgkmlx/218/1860/index_74%s.html'},
        {'type': u'其他', 'page': '67', 'url': 'http://www.huhhot.gov.cn/zwgk/zfxxgkzl/zfxxgkmlx/218/226/index_74%s.html'},
    ]

    page_domain = "http://www.huhhot.gov.cn/zwgk/zfxxgkzl/zfxxgkmlx%s"

    def parse(self, response):
        send_requests = []

        for item in self.fgparamlist:
            page = int(item['page'])
            listurl = item['url']
            for index in range(1, page + 1):
                if index==1:
                    newurl = listurl % ''
                    send_requests.append(scrapy.Request(newurl, callback=self.parse_list, method='get', errback=self.handle_error,meta={'type': item['type']}, ))
                else:
                    p=index-1;
                    newurl=listurl % '_%s' % p
                    send_requests.append(scrapy.Request(newurl, callback=self.parse_list, method='get', errback=self.handle_error,meta={'type': item['type']}, ))

        return send_requests

    def parse_list(self, response):
        for item in response.css("#tbStu td a"):
            detail_url =  self.page_domain % ''.join(item.css("::attr(href)").extract()).replace('../..','')
            yield scrapy.Request(detail_url, callback=self.parse_detail, method='get',errback=self.handle_error,meta={'type': response.meta['type']})
        pass

    def parse_detail(self,response):
        item = {}
        title = ''.join(response.css('.zwgkxl_content h3::text').extract())
        if title != '':
            item['title'] = title
            item['anNo'] = ''.join(response.css('.xxgk_tlb tr:nth-child(2) td:nth-child(4)::text').extract())
            item['pubish_time'] = ''.join(response.css('.xxgk_tlb tr:nth-child(2) td:nth-child(6)::text').extract())
            item['effect_time'] = ''.join(response.css('.xxgk_tlb tr:nth-child(3) td:nth-child(6)::text').extract())
            item['pubish_org'] = ''.join(response.css('.xxgk_tlb tr:nth-child(3) td:nth-child(2)::text').extract())
            item['level'] = self.level
            item['time_liness'] = u"现行有效"
            content = ''.join(response.css('.trs_word').extract())
            item["content"] = re.sub('((class|style|color|href|target|align|title)="[^"]*?")|(<img .*?>)', '',content)  # 内容'''
            #item["content"] = ''
            item['url'] = response.url
            item["provinceName"] = self.provinceName
            item["cityName"] = self.cityName
            item["provinceCode"] = self.provinceCode
            item["cityCode"] = self.cityCode
            item['sIndex'] = ''.join(response.css('.xxgk_tlb tr:nth-child(2) td:nth-child(2)::text').extract())
            item["sTypeName"] = response.meta["type"]
            item['source'] = u"呼和浩特市人民政府"
            # 是否导入正式数据库
            item['export'] = '0'
            item['collection'] = 'fagui'
            item["Id"] = str(uuid.uuid1()).replace('-', '')
            return item

    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)