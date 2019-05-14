#!/usr/bin/python
#-*- coding: utf-8 -*-
import re
import uuid
import json
import scrapy
from dal.service.LawWritData import LawWritData
import random

class LawWritSpider(scrapy.Spider):
    # 华律网法律文书

    name = "lawwrit"
    p_time='2019-04-25'

    allowed_domains=["www.66law.cn"]

    start_urls = [ 'https://www.66law.cn/lawwrit/']

    page_domain = "https://www.66law.cn%s"

    # 初始化打开数据库
    def __init__(self):
        print "spider start..........................."
        super(LawWritSpider, self).__init__(self)
        self.lawWritData = LawWritData()

    def parse(self, response):
        send_requests = []

        for item in response.css(".fl_nr li"):
            url =self.page_domain % ''.join(item.css("a::attr(href)").extract())
            type= ''.join(item.css("a strong::text").extract())
            #插入菜单
            uid = str(uuid.uuid1()).replace('-', '')
            self.lawWritData.insert_lawwrit_menu((uid, type,0,0))
            send_requests.append(scrapy.Request(url, callback=self.parse_list, method='get', errback=self.handle_error,meta={'parentId': uid}))

        return send_requests

    def parse_list(self, response):
        for item in response.css(".ht_b li a"):
            detail_url = self.page_domain % ''.join(item.css("::attr(href)").extract()).replace('../..', '')
            yield scrapy.Request(detail_url, callback=self.parse_detail, method='get', errback=self.handle_error,meta={'parentId': response.meta["parentId"]})

        #处理分页
        nexturl = self.page_domain % ''.join(response.xpath(".//div[@class='page']/a[last()-1]/@href").extract())
        if nexturl<>'javascript:':
           yield scrapy.Request(nexturl, callback=self.parse_list, method='get', errback=self.handle_error,meta={'parentId': response.meta["parentId"]})

        pass


    def parse_detail(self,response):
        item = {}
        title = ''.join(response.css('.xx_bt h1::text').re('[^\s+]'))
        if title != '':
            item['title'] = title
            item['time'] = ''.join(response.css('.xx_bt span i:nth-child(1)::text').extract()).replace('时间：','')
            content = ''.join(response.css('.xx_nr').extract())
            item["content"] = re.sub('((class|style|color|href|target|align|title)="[^"]*?")|(<img .*?>)', '',content)  # 内容'''
            item['url'] = response.url
            item["parentId"] = response.meta["parentId"]
            item["id"] = str(uuid.uuid1()).replace('-', '')

            dcount=random.randint(500,3000)
            vcount = random.randint(3000, 15000)

            self.lawWritData.insert_lawwrit((item["id"],item["parentId"],item["content"],item['title'],item['time'],item['url'],dcount,vcount))

            del item['content']
            print item


    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)