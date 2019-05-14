#!/usr/bin/python
#-*- coding: utf-8 -*-
import re
import uuid
import scrapy
import os
import json
from devops import scrapyd_deploy
from devops import scrapyd_scheduling
from datetime import  datetime
from  dal.service.StatuteData import StatuteData
class WYFGSpider(scrapy.Spider):
    """中国法院网法规"""

    name = "chinalawfagui"
    statuteData = StatuteData()
    allowed_domains=["www.chinalaw.gov.cn"]


    start_urls = [
        'http://www.chinalaw.gov.cn',
        ]
    page_domain = "http://www.chinalaw.gov.cn%s"


    def parse(self, response):
        rqs=[]
        with  open(os.path.abspath('./chinalawData.json'),'r') as f:
            line = json.load(f)
            rqs.extend( self.parse_list(u"国家法律法规", line["fvfg"]))
            rqs.extend(self.parse_list(u"地方法规", line["df"]))
            rqs.extend(self.parse_list(u"行业团体规定", line["xztt"]))
            rqs.extend(self.parse_list(u"部门规章", line["bumen"]))
        return rqs
    def parse_list(self,level,source):
        for item in source:
            yield  scrapy.Request(self.page_domain % item["infostaticurl"], callback=self.parse_detail, method='get',
                                                errback=self.handle_error,meta={'level':level,'title':item["listtitle"],'pub_time':item["releasedate"]})



    def parse_detail(self,response):
        item = {}
        title =response.meta['title']
        if  title!='':
           item['title'] = title
           item['anNo']=None
           item['pubish_time'] = response.meta['pub_time']
           item['effect_time'] = response.meta['pub_time']
           item['pubish_org'] = None
           item['level']= response.meta['level']
           item['time_liness'] = "现行有效"
           content = ''.join(response.xpath('//div[@id="content"]/span').extract())
           item["content"] =re.sub('((class|style|color|href|target|align|title)="[^"]*?")|(<img .*?>)', '', content)  # 内容'''
           item['url'] = response.url
           item['source'] = u"中国政府法制信息网"
           # 是否导入正式数据库
           item['export'] = '0'
           item['collection'] = 'fagui'
           uid=str(uuid.uuid1()).replace('-', '')
           #Id,Time_liness,Effect_time,Level,Pubish_time,Title,AnNo,Source,Pubish_org,Content,IsBuild
           self.statuteData.insert_statute((uid,u'现行有效',item['effect_time'],item['level'],item['pubish_time'],item['title'],item['anNo'],item['source'],item['pubish_org'],item["content"],0))
           del item["content"]
           print item



    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)


