#!/usr/bin/python
#-*- coding: utf-8 -*-
import re
import uuid
import json
import scrapy
from  dal.service.StatuteData import StatuteData

class TongLiaoSpider(scrapy.Spider):
    #  通辽市政府网

    name = "tongliao"
    statuteData = StatuteData()

    provinceName = u"内蒙古"
    cityName = u"通辽市"
    provinceCode='15'
    cityCode='1508'
    level = u"地方法规"
    pubish_time='2019-04-23'

    allowed_domains=["www.tongliao.gov.cn"]

    start_urls = [ 'http://www.tongliao.gov.cn/tl/ztfl/gkml.shtml']

    page_domain = "http://www.tongliao.gov.cn%s"

    fgparamlist = [
        {'type': u'决定', 'page': '41', 'url': 'http://www.tongliao.gov.cn/xxgk/xxgktree/list.jsp?wz=4f023e3455c2427d9a779bf9d5609b58&parentChannelId=402881a06053e512016053e51cfd0087&page=%d'},
        {'type': u'报告', 'page': '4', 'url': 'http://www.tongliao.gov.cn/xxgk/xxgktree/list.jsp?wz=6c32e4a797504bf794249ca2282780bb&parentChannelId=402881a06053e512016053e51cfd0087&page=%d'},
        {'type': u'公告', 'page': '1', 'url': 'http://www.tongliao.gov.cn/xxgk/xxgktree/list.jsp?wz=a2f5809614104fae871ffbe92629f036&parentChannelId=402881a06053e512016053e51cfd0087&page=%d'},
        {'type': u'通告', 'page': '2', 'url': 'http://www.tongliao.gov.cn/xxgk/xxgktree/list.jsp?wz=6d92ebf491f445578629f29ae2d00acc&parentChannelId=402881a06053e512016053e51cfd0087&page=%d'},
        {'type': u'意见', 'page': '9', 'url': 'http://www.tongliao.gov.cn/xxgk/xxgktree/list.jsp?wz=4d89a2fd76de4fb1a81eecad0ff3db1a&parentChannelId=402881a06053e512016053e51cfd0087&page=%d'},
        {'type': u'通知', 'page': '59','url': 'http://www.tongliao.gov.cn/xxgk/xxgktree/list.jsp?wz=f50f51364fc9455181011222b2a67809&parentChannelId=402881a06053e512016053e51cfd0087&page=%d'},
        {'type': u'通报', 'page': '5', 'url': 'http://www.tongliao.gov.cn/xxgk/xxgktree/list.jsp?wz=183816bd4c9843ab8ff177ccbd715321&parentChannelId=402881a06053e512016053e51cfd0087&page=%d'},
        {'type': u'批复', 'page': '1','url': 'http://www.tongliao.gov.cn/xxgk/xxgktree/list.jsp?wz=93b71c1c6c624b059abfa9fb59f43990&parentChannelId=402881a06053e512016053e51cfd0087&page=%d'},
        {'type': u'其他', 'page': '32','url': 'http://www.tongliao.gov.cn/xxgk/xxgktree/list.jsp?wz=8424888c9d614124ac179e6e0fd8569a&parentChannelId=402881a06053e512016053e51cfd0087&page=%d'},
    ]

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
        for item in response.css(".dataList td a"):
            detail_url =  self.page_domain % ''.join(item.css("::attr(href)").extract()).replace('../..','')
            yield scrapy.Request(detail_url, callback=self.parse_detail, method='get',errback=self.handle_error,meta={'type': response.meta['type']})
        pass


    def parse_detail(self,response):
        item = {}
        title = ''.join(response.css('.textc::text').re('[^\s+]'))
        if title != '':
            item['title'] = title
            anNo = ''.join(response.css('.detail_ysj:nth-child(5) em::text').extract())
            if anNo == '':
                anNo = None
            item['anNo'] = anNo
            item['pubish_time'] = ''.join(response.css('.detail_ysj:nth-child(7) em::text').extract())
            item['effect_time'] = None
            item['pubish_org'] = ''.join(response.css('.detail_ysj:nth-child(2) em::text').extract())
            item['level'] = self.level
            item['time_liness'] = u"现行有效"
            content = ''.join(response.css('#text01').extract())
            item["content"] = re.sub('((class|style|color|href|target|align|title)="[^"]*?")|(<img .*?>)', '',content)  # 内容'''
            #item["content"] = ''
            item['url'] = response.url
            item["provinceName"] = self.provinceName
            item["cityName"] = self.cityName
            item["provinceCode"] = self.provinceCode
            item["cityCode"] = self.cityCode
            item['sIndex'] = ''.join(response.css('.detail_ysj:nth-child(1) em::text').extract())
            item["sTypeName"] = response.meta["type"]
            item['source'] = u"通辽市人民政府"
            # 是否导入正式数据库
            item['export'] = '0'
            item['collection'] = 'fagui'
            item["Id"] = str(uuid.uuid1()).replace('-', '')
            return item


    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)