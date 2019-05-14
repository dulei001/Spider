#!/usr/bin/python
#-*- coding: utf-8 -*-
import re
import uuid
import json
import scrapy
from  dal.service.StatuteData import StatuteData

class BYNRSpider(scrapy.Spider):
    #  巴彦淖尔市人民政府

    name = "bynr"
    statuteData = StatuteData()

    provinceName = u"内蒙古"
    cityName = u"巴彦淖尔市"
    provinceCode='15'
    cityCode='1502'
    level = u"地方法规"
    pubish_time='2019-04-24'

    allowed_domains=["www.bynr.gov.cn"]

    start_urls = [ 'http://www.bynr.gov.cn/xxgk/zwgkml/']

    page_domain = "http://www.bynr.gov.cn/xxgk/zwgkml/%s"

    def parse(self, response):
        send_requests = []
        pageSize=19;

        for item in response.css('.cont_left_zwgk_cont_foot ul li'):
            url = ''.join(item.css("a::attr(href)").extract())
            url=url.replace('../','').replace('./','')
            type=''.join(item.css("a::text").extract()).replace(' ','')
            dcount=''.join(item.css("::text").extract()).replace(' ','')
            dcount= re.findall("\d+",dcount)[0]
            page= (int(dcount) + pageSize - 1) / pageSize;

            for index in range(1, page + 1):
                if index==1:
                    send_requests.append(scrapy.Request(self.page_domain % url, callback=self.parse_list, method='get', errback=self.handle_error ,meta={'sublevel': url}))
                else:
                    p=index-1
                    newurl=''.join((url, 'index_%d.html' % p ))
                    send_requests.append(scrapy.Request(self.page_domain % newurl, callback=self.parse_list, method='get', errback=self.handle_error ,meta={'sublevel': url}))

        return send_requests

    def parse_list(self, response):
        sublevel=response.meta['sublevel']
        for item in response.css(".cont_right_cont a"):
            detail_url=''.join((sublevel , ''.join(item.css("::attr(href)").extract()).replace('./','')))
            yield scrapy.Request(self.page_domain % detail_url, callback=self.parse_detail, method='get',errback=self.handle_error)
        pass

    def parse_detail(self, response):
        item = {}
        title = ''.join(response.css('.zwgk_hei18::text').extract_first())
        if title != '':
            item['title'] = title
            item['anNo'] =''.join(response.css('.cont_right_cont_xilan table:nth-child(1) tr:nth-child(4) td:nth-child(2)::text').re('[^\s+]'))
            item['pubish_time'] =''.join(response.css('.cont_right_cont_xilan table:nth-child(1) tr:nth-child(2) td:nth-child(4)::text').re('[^\s+]'))
            item['effect_time'] = None
            item['pubish_org'] = ''.join(response.css('.cont_right_cont_xilan table:nth-child(1) tr:nth-child(2) td:nth-child(2)::text').extract())
            item['level'] = self.level
            item['time_liness'] = u"现行有效"
            content = ''.join(response.css('.cont_right_cont_xilan table:nth-child(2) table:nth-child(2)').extract())
            item["content"] = re.sub('((class|style|color|href|target|align|title)="[^"]*?")|(<img .*?>)|(?i)(<SCRIPT)[\\s\\S]*?((</SCRIPT>)|(/>))|(?i)(<style)[\\s\\S]*?((</style>)|(/>))', '',content)  # 内容'''
            #item["content"] = ''
            item['url'] = response.url
            item["provinceName"] = self.provinceName
            item["cityName"] = self.cityName
            item["provinceCode"] = self.provinceCode
            item["cityCode"] = self.cityCode
            item['sIndex'] = ''.join(response.css('.cont_right_cont_xilan table:nth-child(1) tr:nth-child(1) td:nth-child(2)::text').extract_first())

            #判断文件类型
            stype=''
            if '通知' in title:
                stype=u'通知'
            elif '通告' in title:
                stype=u'通告'
            elif '批复' in title:
                stype = u'批复'
            elif '命令' in title:
                stype = u'命令'
            elif '通报' in title:
                stype = u'通报'
            elif '意见' in title:
                stype = u'意见'
            elif '决定' in title:
                stype = u'决定'
            elif '公告' in title:
                stype = u'公告'
            else:
                stype = u'其他'

            item["sTypeName"] = stype
            item['source'] = u"巴彦淖尔市人民政府"
            # 是否导入正式数据库
            item['export'] = '0'
            item['collection'] = 'fagui'
            item["Id"] = str(uuid.uuid1()).replace('-', '')
            return item


    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)