#!/usr/bin/python
# -*- coding: utf-8 -*-

import scrapy
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import json
import urllib2
from lawyer.items.newCaiPan_item import NewCaiPanItem
import time

class BeiJingCaiPanSpider(scrapy.Spider):
    name = "beijing_caipan_spider"
    allowed_domains = ['www.bjcourt.gov.cn']

    #  入口
    start_urls = ["http://www.bjcourt.gov.cn/cpws/index.htm"]

    def parse(self, response):
        #处理分页--总页数38526
        for p in range(1, 38526,1):
            url = "http://www.bjcourt.gov.cn/cpws/index.htm?page=%d" % p
            yield scrapy.Request(url, callback=self.pagelist_parse, errback=self.handle_error)

    def pagelist_parse(self, response):
        url="http://www.bjcourt.gov.cn"
        for li in response.xpath("//ul[@class='ul_news_long']/li"):
            durl = url + ''.join(li.xpath('a/@href').extract())
            yield scrapy.Request(durl, callback=self.detail_parse, errback=self.handle_error)

    def detail_parse(self, response):
        print u"详情页==="+response.url

        title= ''.join(response.xpath("//h3[@class='h3_22_m_blue']/text()").extract())
        tdinput = response.xpath("//div[@class='fd-article-infor']/table/tr/td/input/@value").extract()

        fayuan = tdinput[0]
        ctype = tdinput[1]
        anyou = tdinput[2]
        wstype = tdinput[3]
        anhao = tdinput[4]
        cptime=tdinput[5]

        content = ''.join(response.xpath("//div[@id='cc']").extract())
        startstr = '<p class=MsoNormal';
        endstr = '</div>';
        bindex = content.index(startstr)
        eindex = content.index(endstr)
        wscontnet = content[bindex:eindex]

        model = NewCaiPanItem()
        model["url"] = response.url
        model["title"] = title
        model["fanyuan"] = fayuan
        model["anhao"] = anhao
        model["anyou"] = anyou

        type_vail = ''
        doctype_vail = ''
        if u'刑事' in ctype:
            type_vail = u'刑事案件'
        elif u'民事' in ctype:
            type_vail = u'民事案件'
        elif u'行政' in ctype:
            type_vail = u'行政案件'
        elif u'赔偿' in ctype:
            type_vail = u'赔偿案件'
        elif u'执行' in ctype:
            type_vail = u'执行案件'
        else:
            type_vail = u'其他案件'

        if u'判决' in wstype:
            doctype_vail = u'判决书'
        elif u'裁定' in wstype:
            doctype_vail = u'裁定书'
        elif u'通知' in wstype:
            doctype_vail = u'通知书'
        elif u'决定' in wstype:
            doctype_vail = u'决定书'
        elif u'调节' in wstype:
            doctype_vail = u'调节书'
        elif u'令' in wstype:
            doctype_vail = u'令'
        else:
            doctype_vail = u'其他'
        # 案件类型
        model["type"] = type_vail
        # 文书类型
        model["doctype"] = doctype_vail
        # 发布时间
        model["stime"] = cptime
        model["content"] = wscontnet
        model["createtime"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        model["source"] = u"北京法院审判信息网"
        return model


    def handle_error(self, result, *args, **kw):
        self.logger.error("error url is :%s" % result.request.url)