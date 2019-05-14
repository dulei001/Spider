#!/usr/bin/python
# -*- coding: utf-8 -*-

import scrapy
import time
from lawyer.items.newCaiPan_item import NewCaiPanItem

class ChongQingCaiPanSpider(scrapy.Spider):
    name = "chongqing_caipan_spider"
    allowed_domains = ['www.cqfygzfw.com']
    #  分别一次

    start_urls = ["http://www.cqfygzfw.com/court/html/1/cpwsAction_getfllist_1.html",
                  "http://www.cqfygzfw.com/court/html/2/cpwsAction_getfllist_1.html",
                  "http://www.cqfygzfw.com/court/html/6/cpwsAction_getfllist_1.html",
                  "http://www.cqfygzfw.com/court/html/7/cpwsAction_getfllist_1.html",
                  "http://www.cqfygzfw.com/court/html/8/cpwsAction_getfllist_1.html"
                  ]
    # 用于测试  start_urls = ["http://www.cqfygzfw.com/court/html/1/cpwsAction_getfllist_1.html"]

    def parse(self, response):
        # 总页数6092
        #根据链接获取页码
        _url=str(response.url)
        url_arr= _url.split('/')
        # 1 刑事案件 6092  2 民事案件 37048  6 行政案件 1733  7 赔偿案件 80 8 执行案件 1310
        _page = 0
        _intType = int(url_arr[-2])
        if _intType == 1:
            _page = 6093
        elif _intType == 2:
            _page = 37049
        elif _intType == 6:
            _page = 1734
        elif _intType == 7:
            _page = 81
        elif _intType == 8:
            _page = 1311

        #用于测试  _page = 2
        for num in range(1, _page):
            yield scrapy.Request(url='http://www.cqfygzfw.com/court/html/'+url_arr[-2]+'/cpwsAction_getfllist_' + str(num) + '.html',
                                 method='GET',
                                 dont_filter=True,
                                 callback=self.pase_item,
                                 errback=self.handle_error)


    def pase_item(self, response):
         item_urls=response.xpath('//table[3]/tr/td[2]/div/a/@href').extract()
         for item_url in item_urls:
            yield scrapy.Request(url='http://www.cqfygzfw.com' + item_url, callback=self.pase_item_details)

    def pase_item_details(self, response):
        model = {}
        #标题
        title = ''.join(response.xpath('/html/body/div[4]/div[2]/h1/text()').extract())
        # 发布时间
        stime = ''.join(response.xpath('//*[@id="wsTime"]/span/text()').extract())
        stime = stime.replace(u'提交时间：', '')
        #获取内容的html 页面
        body_str = ''.join(response.xpath('/html/body').extract())
        pp_index = body_str.index('var htm =')
        _s = pp_index + 11
        _e = pp_index + 60
        # 内容的html
        str = body_str[_s: _e]
        _strUrl = str.split(';')[0].replace('"', "")
        _htm_url = "http://www.cqfygzfw.com"+_strUrl
        yield scrapy.Request(url=_htm_url, callback=self.pase_item_html,meta = {"title": title, "stime": stime})

    def pase_item_html(self, response):
         stime =response.meta['stime']
         title = response.meta['title']
         model = NewCaiPanItem()
         model["url"]=response.url
         model["title"]= title
         model["fanyuan"]=''.join(response.xpath('/html/body/p[1]/span/text()').extract())
         model["anhao"]=''.join(response.xpath('/html/body/p[4]/span/text()').extract())
         model["anyou"] = ''
         typestr = ''.join(response.xpath('/html/body/p[2]/span/text()').extract())
         if typestr.strip()=="":
             typestr = ''.join(response.xpath('/html/body/p[3]/span/text()').extract())

         type_vail=''
         doctype_vail =''
         if u'刑事' in typestr:
             type_vail=u'刑事案件'
         elif u'民事' in typestr:
             type_vail=u'民事案件'
         elif u'行政' in typestr:
             type_vail = u'行政案件'
         elif u'赔偿' in typestr:
             type_vail = u'赔偿案件'
         elif u'执行' in typestr:
             type_vail = u'执行案件'
         else:
             type_vail=u'其他案件'

         if u'判决' in typestr:
             doctype_vail = u'判决书'
         elif u'裁定' in typestr:
             doctype_vail = u'裁定书'
         elif u'通知' in typestr:
             doctype_vail = u'通知书'
         elif u'决定' in typestr:
             doctype_vail = u'决定书'
         elif u'调节' in typestr:
             doctype_vail = u'调节书'
         elif u'令' in typestr:
            doctype_vail = u'令'
         else:
             doctype_vail = u'其他'
         #案件类型
         model["type"] = type_vail
         #文书类型
         model["doctype"] =doctype_vail
         model["shenliApp"]=""
         #发布时间
         model["stime"] = stime
         model["content"] =''.join( response.xpath('/html/body').extract())
         model["createtime"] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
         model["source"] = u"重庆法院公众服务网"

         return  model


    def handle_error(self, result, *args, **kw):
          print "error url is :%s" % result.request.url
          self.logger.error("error url is :%s" % result.request.url)


