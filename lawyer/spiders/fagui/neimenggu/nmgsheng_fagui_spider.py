#!/usr/bin/python
#-*- coding: utf-8 -*-
import re
import uuid
import json
import scrapy
from  dal.service.StatuteData import StatuteData

class NMGShengSpider(scrapy.Spider):
    # 内蒙古自治区人民政府网

    name = "nmgsheng"
    statuteData = StatuteData()

    provinceName = u"内蒙古"
    provinceCode = '15'
    level = u"地方法规"
    pubish_time = '2019-04-23'

    allowed_domains=["www.nmg.gov.cn"]

    start_urls = ['http://www.nmg.gov.cn/col/col4191/index.html']

    fgparamlist=[
        {'type': u'决定', 'page': '2', 'params': {'infotypeId': '0', 'jdid': '2', 'nServiceid': '13', 'vc_bm': 'NC1', 'area': '1115000001151201XD'}},
        {'type': u'命令', 'page': '3','params': {'infotypeId': '0', 'jdid': '2', 'nServiceid': '14', 'vc_bm': 'NC2', 'area': '1115000001151201XD'}},
        {'type': u'通报', 'page': '3', 'params': {'infotypeId': '0', 'jdid': '2', 'nServiceid': '17', 'vc_bm': 'NC5', 'area': '1115000001151201XD'}},
        {'type': u'意见', 'page': '20','params': {'infotypeId': '0', 'jdid': '2', 'nServiceid': '18', 'vc_bm': 'NC6', 'area': '1115000001151201XD'}},
        {'type': u'批复', 'page': '1', 'params': {'infotypeId': '0', 'jdid': '2', 'nServiceid': '19', 'vc_bm': 'NC7', 'area': '1115000001151201XD'}},
        {'type': u'通知', 'page': '89', 'params': {'infotypeId': '0', 'jdid': '2', 'nServiceid': '20', 'vc_bm': 'NC8', 'area': '1115000001151201XD'}},
        {'type': u'公告', 'page': '1','params': {'infotypeId': '0', 'jdid': '2', 'nServiceid': '23', 'vc_bm': 'NC11', 'area': '1115000001151201XD'}},
        {'type': u'通告', 'page': '2', 'params': {'infotypeId': '0', 'jdid': '2', 'nServiceid': '24', 'vc_bm': 'NC12', 'area': '1115000001151201XD'}},
        {'type': u'其他', 'page': '1','params': {'infotypeId': '0', 'jdid': '2', 'nServiceid': '26', 'vc_bm': 'NC14', 'area': '1115000001151201XD'}}
    ]

    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
    }

    def parse(self, response):
        send_requests = []

        for item in self.fgparamlist:
            page=int(item['page']);
            for index in range(1,page+1):
                url="http://www.nmg.gov.cn/module/xxgk/serviceinfo.jsp?currpage=%d" % index;
                send_requests.append(scrapy.FormRequest(url=url,
                                                        method="POST",
                                                        formdata=item['params'],
                                                        headers=self.headers,
                                                        callback=self.parse_list,
                                                        meta={'type': item['type']},
                                                        errback=self.handle_error))
        return send_requests


    def parse_list(self,response):
        for item in response.css('table a[href*="http://www.nmg.gov.cn"]'):
            url= ''.join(item.css("::attr(href)").extract()).replace('../..','')
            yield scrapy.Request(url, callback=self.parse_detail, method='get',errback=self.handle_error,meta={'type': response.meta['type']})


    def parse_detail(self,response):
        item = {}
        title = ''.join(response.css('.main-fl-tit::text').re('[^\s+]'))
        if title != '':
            item['title'] = title
            item['anNo'] = ''.join(response.css('.xxgk_table tr:nth-child(3) td:nth-child(2)::text').re('[^\s+]'))
            item['pubish_time'] = ''.join(response.css('.xxgk_table tr:nth-child(2) td:nth-child(4)::text').re('[^\s+]'))
            item['effect_time'] = None
            item['pubish_org'] = ''.join(response.css('.xxgk_table tr:nth-child(2) td:nth-child(2)::text').re('[^\s+]'))
            item['level'] = self.level
            item['time_liness'] = u"现行有效"
            content = ''.join(response.css('#zoom').extract())
            item["content"] = re.sub('((class|style|color|href|target|align|title)="[^"]*?")|(<img .*?>)', '',content)  # 内容'''
            #item["content"] = ''
            item['url'] = response.url
            item["provinceName"] = self.provinceName
            item["provinceCode"] = self.provinceCode
            item["cityName"] = None
            item["cityCode"] = None
            item['sIndex'] = ''.join(response.css('.xxgk_table tr:nth-child(1) td:nth-child(2)::text').extract())
            item["sTypeName"] = response.meta["type"]
            item['source'] = u"内蒙古自治区人民政府"
            # 是否导入正式数据库
            item['export'] = '0'
            item['collection'] = 'fagui'
            item["Id"] = str(uuid.uuid1()).replace('-', '')
            return item

        pass


    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)