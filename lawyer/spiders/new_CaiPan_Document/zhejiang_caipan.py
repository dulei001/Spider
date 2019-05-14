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

class ZheJiangCaiPanSpider(scrapy.Spider):
    name = "zhejiang_caipan_spider"
    allowed_domains = ['www.zjsfgkw.cn']

    #  入口
    start_urls = ["http://www.zjsfgkw.cn/Document/JudgmentBook"]

    def parse(self, response):
        baseurl = "http://www.zjsfgkw.cn/document/JudgmentSearch"
        #获取案件类型
        caseType = response.xpath("//ul[@id='ulajlb']/li/a/text()").extract();
        #获取法院编号
        fayuan = response.xpath("//ul[@class='courtNameDropMenu']/li/@fyid").extract();

        #print u"案件类型长度---------"+str(len(caseType))
        #print  u"法院编号长度---------"+str(len(fayuan))

        url_items = []

        #只能访问1000页的数据
        for ctype in caseType:
            if ctype=="全部":
                continue
            for fy in fayuan:
                for p in range(1,1001):
                    detail_request = scrapy.FormRequest(url=baseurl,
                                                        method="POST",
                                                        callback=self.parseList,
                                                        errback=self.handle_error,
                                                        formdata={"pageno": str(p),"pagesize":str(10),"ajlb":str(ctype),"cbfy":str(fy),"jarq1":"20070101","jarq2":"20170901"})
                    yield detail_request

    def parseList(self,response):
        print u"搜索----------" + response.url
        data = json.loads(response.body_as_unicode())
        #print data
        url_items = []
        datalist = data['list']
        for item in datalist:
            #print "DocumentId============"+str(item['DocumentId'])
            AH = item['AH']
            AJLB = item['AJLB']
            CourtName = item['CourtName']
            JARQ = item['JARQ']
            detail_request=scrapy.Request(url='http://www.zjsfgkw.cn/document/JudgmentDetail/%d' % item['DocumentId'],
                                          callback=self.pase_details,
                                          errback=self.handle_error,
                                          meta={"AH": AH, "AJLB": AJLB, "CourtName": AH, "CourtName": CourtName, "JARQ": JARQ})
            url_items.append(detail_request)
        return url_items

    def pase_details(self,response):
        #获取iframe上的url链接
        AH =  response.meta['AH']
        AJLB =  response.meta['AJLB']
        CourtName = response.meta['CourtName']
        JARQ =  response.meta['JARQ']
        detailurl = response.xpath("//div[@class='books_detail_content']/iframe/@src").extract()[0];
        print u"详情iframe----------"+str(detailurl)
        yield scrapy.Request(url='http://www.zjsfgkw.cn/'+detailurl,
                             callback=self.pase_details_iframe,
                             errback=self.handle_error,
                             meta={"AH": AH, "AJLB": AJLB, "CourtName": AH, "CourtName": CourtName, "JARQ": JARQ})

    def pase_details_iframe(self, response):
        detailurl = response.url
        print u"文书详情----------" + str(detailurl)

        AH = response.meta['AH'] #标题  例：（2017）浙0108执1206号
        AJLB = response.meta['AJLB']  #文书类型  例：执行
        CourtName = response.meta['CourtName']  #法院名称
        JARQ = response.meta['JARQ'] #时间

        wstypename = ''.join(response.xpath("/html/body/div/p[3]/span/text()").extract())

        model = NewCaiPanItem()
        model["url"] = response.url
        model["title"] = AH
        model["fanyuan"] = CourtName
        model["anhao"] = AH
        model["anyou"] = ''

        type_vail = ''
        doctype_vail = ''
        if u'刑事' in AJLB:
            type_vail = u'刑事案件'
        elif u'民事' in AJLB:
            type_vail = u'民事案件'
        elif u'行政' in AJLB:
            type_vail = u'行政案件'
        elif u'赔偿' in AJLB:
            type_vail = u'赔偿案件'
        elif u'执行' in AJLB:
            type_vail = u'执行案件'
        else:
            type_vail = u'其他案件'

        if u'判决' in wstypename:
            doctype_vail = u'判决书'
        elif u'裁定' in wstypename:
            doctype_vail = u'裁定书'
        elif u'通知' in wstypename:
            doctype_vail = u'通知书'
        elif u'决定' in wstypename:
            doctype_vail = u'决定书'
        elif u'调节' in wstypename:
            doctype_vail = u'调节书'
        elif u'令' in wstypename:
            doctype_vail = u'令'
        else:
            doctype_vail = u'其他'
        # 案件类型
        model["type"] = type_vail
        # 文书类型
        model["doctype"] = doctype_vail
        # 发布时间
        model["stime"] = JARQ
        model["content"] = ''.join(response.xpath('/html/body').extract())
        model["createtime"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        model["source"] = u"浙江法院公开网"
        return model


    def handle_error(self, result, *args, **kw):
        self.logger.error("error url is :%s" % result.request.url)