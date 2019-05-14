#!/usr/bin/python
# -*- coding: utf-8 -*-
import base64
import json
import scrapy
import re

import zlib
from scrapy.spiders import Spider

class Jufa_FaguiSpider(Spider):
    name = "jufa_fagui_spider"
    allowed_domains = ['www.jufaanli.com']
    start_urls = [
        "http://www.jufaanli.com" #法律分类
    ]
    # 爬虫入口
    def parse(self, response):
        baseurl = "http://www.jufaanli.com/home/searchLaw/searchLawJson"
        totalPage = (1385790 - 1) / (20 + 1)
        for num in range(1, totalPage):
            yield scrapy.FormRequest(url=baseurl,
                                                method="POST",
                                                callback=self.parsr_list,
                                                meta={"dont_redirect": True},
                                                errback=self.handle_error,
                                                formdata={"page": str(num),"searchNum":str(20)})

    #解析列表
    def parsr_list(self,response):
        res_uuid= json.loads(response.body_as_unicode())
        info = res_uuid["info"]["searchList"]["list"]
        for var_uuid in info:
          url_detail =  "http://www.jufaanli.com/lawdetail/"+ str(var_uuid["uuid"])
          yield scrapy.Request(url=url_detail,
                               method='GET',
                               dont_filter=True,
                               meta={"xljb":var_uuid["xljb"],"label":var_uuid["label"],"title":var_uuid["title"]},
                               callback=self.parse_detail,
                               errback=self.handle_error)

    #解析法规详情页面
    def parse_detail(self,response):
        model = {};
        model["title"]=response.meta["title"] #标题
        model["level"]=response.meta["xljb"] #效力级别
        model["publishunit"]=response.meta["label"][0] #发布单位
        model["dispatchno"]=response.meta["label"][1] #发文字号
        model["publishtime"] = response.meta["label"][2].replace(u'发布','')  #颁布时间
        model["effecttime"] = response.meta["label"][3].replace(u'实施','')  # 生效时间
        model["state"] = response.meta["label"][4]  # 状态
        subtext = ''.join(response.xpath('//*[@class="jufa-detail-ietm"]').extract())
        content =  ''.join(response.xpath('//*[@id="caseText"]/div[2]').extract()).replace(subtext,'')
        model["content"] =re.sub('(class|name|id)="[^"]*?"','', content) #内容
        model['collection'] = 'fagui'
        model['source'] = '聚法网'
        model["url"] = response.url
        #model["html"] =base64.b64encode(zlib.compress(response.text.encode("utf-8")))
        return model

    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)





