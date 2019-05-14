#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

import scrapy
from lawyer.items.LawyerInfo_item import  LawyerInfoItem
from scrapy.spiders import Spider
class GuiZhou1Spider(Spider):
    name = "zunyi_spider"
    # 贵州遵义律师
    start_urls = [
        "http://www.zy12348.gov.cn/sites/templateLib/cache/zunYSSFJ/Query.jsp?qid=ff8080814e2356fb014e24db5dc90023"
    ]

    # 爬虫入口
    def parse(self, response):
        baseurl = "http://www.zy12348.gov.cn/QG/paginQueryByParameterNoLogin.action"
        for i in range(1, 25):
            formdata={
                 'qg[0][QG_ID]': 'ff8080814e2356fb014e24db5dc90023',
                 'qg[0][COLUMN_DB_NAME]': 'ID',
                 'qg[0][COLUMN_ALIAS]':'',
                 'qg[0][COLUMN_QUERY_CONDITION]':'0',
                 'page':str(i),
                 'maxRow':'22',
             }
            yield scrapy.FormRequest(url=baseurl, method="POST",formdata=formdata,callback=self.parse_detail,errback=self.handle_error)


    #律师信息
    def parse_detail(self,response):
        data = json.loads(response.body_as_unicode())
        for x in data['rows']:
                item = LawyerInfoItem()
                item['name'] = x['ID']
                sex=x['xingB']
                if (sex == u"男"):
                    item["sex"] = "0"
                elif (sex == u"女"):
                    item["sex"] = "1"
                else:
                    item["sex"] = ""
                item['personnel_type'] =x['zhiYLB']
                item['firm'] = x['zhiYJG']
                item['lawnumber'] = x['zhiYZH']
                item['get_time'] = ''
                item['start_time'] = ''
                item['province']=u'贵州'
                item['education'] = ''
                item['cert_type'] = ''
                item['headurl'] = ''
                item['ispartnership'] = ''
                item['nation'] = ''
                item['political_status'] = ''
                item['professional_status'] = ''
                item['profession'] = ''
                item['url'] = response.url
                item['collection'] = 'lawyers'
                yield item

    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)





