#!/usr/bin/python
#-*- coding: utf-8 -*-
import re
import uuid
import json
import scrapy
from  dal.service.StatuteData import StatuteData

class XAMSpider(scrapy.Spider):
    # 兴安盟行政公署

    name = "xinganmeng"
    statuteData = StatuteData()

    provinceName = u"内蒙古"
    cityName = u"兴安盟"
    provinceCode='15'
    cityCode='1512'
    level = u"地方法规"
    pubish_time='2019-04-23'

    allowed_domains=["xam.gov.cn"]

    start_urls = [ 'http://www.xam.gov.cn/xam/_300473/_300600/index.html']

    page_domain = "http://www.huhhot.gov.cn/zwgk/zfxxgkzl/zfxxgkmlx%s"

    page_domain = "http://www.xam.gov.cn%s"

    def parse(self, response):
        send_requests = []

        for item in response.css('#tsxa_r a[href^="/xam"]'):
            url = ''.join(item.css("::attr(href)").extract()).replace('../..', '')
            send_requests.append(scrapy.Request(self.page_domain % url, callback=self.parse_list, method='get',errback=self.handle_error ))

        return send_requests

    def parse_list(self, response):
        for item in response.css(".gkml_list a"):
            detail_url = ''.join(item.css("::attr(href)").extract()).replace('../..','')
            yield scrapy.Request(self.page_domain % detail_url, callback=self.parse_detail, method='get',errback=self.handle_error)

        #处理分页
        nexturl =  ''.join(response.css('.gkml_con .page a:nth-child(5)::attr(tagname)').extract()).replace('../..', '')
        if nexturl<>'[NEXTPAGE]':
            yield scrapy.Request(self.page_domain % nexturl, callback=self.parse_list, method='get',errback=self.handle_error)

        pass


    def parse_detail(self, response):
        item = {}
        title = ''.join(response.css('.qzqd_tit::text').re('[^\s+]'))
        if title != '':
            item['title'] = title
            item['anNo'] =''.join(response.css('.xxgk_top li:nth-child(3)::text').re('[^\s+]'))
            item['pubish_time'] =''.join(response.css('.xxgk_top li:nth-child(4)::text').re('[^\s+]')).replace(u"年","-").replace(u"月","-").replace(u"日","")
            item['effect_time'] = None
            item['pubish_org'] = ''.join(response.css('.xxgk_top li:nth-child(2)::text').re('[^\s+]'))
            item['level'] = self.level
            item['time_liness'] = u"现行有效"
            content = ''.join(response.css('.content_xilan').extract())
            item["content"] = re.sub('((class|style|color|href|target|align|title)="[^"]*?")|(<img .*?>)|(?i)(<SCRIPT)[\\s\\S]*?((</SCRIPT>)|(/>))|(?i)(<style)[\\s\\S]*?((</style>)|(/>))', '',content)  # 内容'''
            #item["content"] = ''
            item['url'] = response.url
            item["provinceName"] = self.provinceName
            item["cityName"] = self.cityName
            item["provinceCode"] = self.provinceCode
            item["cityCode"] = self.cityCode
            item['sIndex'] =  ''.join(response.css('.xxgk_top li:nth-child(1)::text').re('[^\s+]'))

            #判断文件类型
            stype=''
            if '通知' in title:
                stype = u'通知'
            elif '通告' in title:
                stype = u'通告'
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
            item['source'] = u"兴安盟行政公署"
            # 是否导入正式数据库
            item['export'] = '0'
            item['collection'] = 'fagui'
            item["Id"] = str(uuid.uuid1()).replace('-', '')
            return item



    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)