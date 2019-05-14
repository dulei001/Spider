#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import time

import scrapy
from lawyer import http_util
from lawyer.items.LawyerInfo_item import  LawyerInfoItem
from scrapy.spiders import Spider
class TianJin_LawyerSpider(Spider):
    name = "tianjin_law_spider"
    start_urls = [
        "http://111.160.0.142:8091/lawyer/home/lawyer-list.html" #天津律师
    ]
    # 爬虫入口
    def parse(self, response):
        baseurl = "http://111.160.0.142:8091/lawyer/lawyerfiles/getLawyerInfo?username=&usersex=&lawyertype=&areacode=&lawofficename=&workcardnum=&officeresult=0&beginage=0&endage=1000&page={0}&pagesize=20"
        for i in range(1, 303):
             yield scrapy.Request(url=baseurl.format((str(i))),
                                                    method="get",
                                                    headers={'X-Requested-With':'XMLHttpRequest'},
                                                    callback=self.parse_list,
                                                    meta={"dont_redirect": True},
                                                    errback=self.handle_error
                                                              )
    #列表
    def parse_list(self,response):
        data = json.loads(response.body_as_unicode())
        for dc in data['data']['items']:
            item = LawyerInfoItem()
            item['name'] = dc['username']
            if dc['usersex']!=None:
                item['sex'] = int(dc['usersex'])
            item['personnel_type'] = self.search_personnel_type(dc['lawyertype'])
            item['firm'] = dc['lawofficename']
            item['lawnumber'] = dc['workcardnum']
            item['get_time'] = ''
            item['start_time'] = '' if dc['practiceyear'] == None else dc['practiceyear']
            item['province'] = u'天津'
            item['education'] = self.search_edu(dc['cultuerlev'])
            item['cert_type'] = ''
            item['headurl'] = ''
            imagesrc =str(dc['image'])
            if imagesrc != '':
                headurl = "http://111.160.0.142:8091/lawyer/resources/photo/" + imagesrc
                item['headurl'] = ''.join(
                    http_util.downloadImage([headurl], 'lawyer_pics/tianjin'))
            item['ispartnership'] = ''
            item['nation'] = ''
            item['political_status'] = ''
            item['professional_status'] = 0 if dc['officeresult'] == "0" else 1
            item['profession'] =''
            item['url'] = 'http://111.160.0.142:8091/lawyer/home/lawyer-detail.html?id={0}'.format((dc['lawyerid']))
            item['collection'] = 'lawyers'
            yield item


    def search_edu(self, s):
        if s!='' or s!='null':
            cultuerlev = ["博士研究生", "硕士研究生", "双学士", "大学本科", "大专", "中专及以下"]
            try:
                return cultuerlev[int(s)]
            except:
                return ''
        else:
            return ''

    def search_personnel_type(self, s):
        if s != '' or s != 'null':
            lawyertype = ["兼职律师", "专职律师", "专职律师（派驻）", "法援律师", "公司律师", "公职律师"]
            try:
                return lawyertype[int(s)]
            except:
                return ''
        else:
            return ''

    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)



