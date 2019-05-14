#!/usr/bin/python
# -*- coding: utf-8 -*-

import scrapy
import time
from lawyer.items.newCaiPan_item import NewCaiPanItem

class ShangHaiCaiPanSpider(scrapy.Spider):
    name = "shanghai_caipan_spider"
    allowed_domains = ['www.hshfy.sh.cn']
    #  分别一次

    start_urls = ["http://www.hshfy.sh.cn/shfy/gweb2017/flws_list.jsp"]

    def parse(self, response):
        #总页数91813
        for num in range(1, 91814):
            yield scrapy.FormRequest(url='http://www.hshfy.sh.cn/shfy/gweb2017/flws_list_content.jsp',
                                     method="POST",
                                     callback=self.pase_item,
                                     errback=self.handle_error,
                                     formdata={"fydm":'',
                                               "ah":'',
                                               "ay":'',
                                               "ajlb":'',
                                               "wslb":'',
                                               "title":'',
                                               "jarqks":'',
                                               "jarqjs":'',
                                               "qwjs":'',
                                               "wssj":'',
                                               "yg":'',
                                               "bg":'',
                                               "spzz":'',
                                               "flyj":'',
                                               "pagesnum":str(num)
                                               })

    def pase_item(self,response):
         model = {}
         item_url_arr=[]

         for tr in response.xpath('//table/tr'):

              model["anhao"]=''.join(tr.xpath('td[1]/text()').extract())
              model["title"] = ''.join(tr.xpath('td[2]/text()').extract())
              model["anyou"] = ''.join(tr.xpath('td[4]/text()').extract())
              model["shenliApp"] = ''.join(tr.xpath('td[6]/text()').extract())
              model["stime"] = ''.join(tr.xpath('td[7]/text()').extract())
              if  model["title"]!=u'标题':
                  _onclick = ''.join(tr.xpath('@onclick').extract())
                  _htm_url_id = _onclick.split("'")[1]
                  _htm_url = "http://www.hshfy.sh.cn/shfy/gweb2017/flws_view.jsp?pa=" + _htm_url_id
                  yield scrapy.Request(url=_htm_url, callback=self.pase_item_html,
                                       meta=model)


    def pase_item_html(self, response):
        url= response.url

        model = NewCaiPanItem()
        model["title"]= response.meta['title']
        model["stime"]=response.meta['stime']
        model["anyou"] = response.meta['anyou']
        model["shenliApp"] = response.meta['shenliApp']
        model["anhao"] = response.meta['anhao']
        #model["content"] = ''.join(response.xpath('//*[@id="wsTable"]').extract())

        model["fanyuan"] = ''.join(response.xpath('//*[@id="wsTable"]/table/tr[1]/td/div/text()').extract()).strip()

        typestr = ''.join(response.xpath('//*[@id="wsTable"]/table/tr[2]/td/div/text()').extract()).strip()
        if typestr.strip() == "":
            typestr = ''.join(response.xpath('/html/body/p[3]/span/text()').extract())

        type_vail = ''
        doctype_vail = ''
        if u'刑事' in typestr:
            type_vail = u'刑事案件'
        elif u'民事' in typestr:
            type_vail = u'民事案件'
        elif u'行政' in typestr:
            type_vail = u'行政案件'
        elif u'赔偿' in typestr:
            type_vail = u'赔偿案件'
        elif u'执行' in typestr:
            type_vail = u'执行案件'
        else:
            type_vail = u'其他案件'

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
        # 案件类型
        model["type"] = type_vail
        # 文书类型
        model["doctype"] = doctype_vail



        model["createtime"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        model["url"]= url
        model["source"] = u"上海高级人民法院网"
        return  model

    def handle_error(self, result, *args, **kw):
         print "error url is :%s" % result.request.url
         self.logger.error("error url is :%s" % result.request.url)