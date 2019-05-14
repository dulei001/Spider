#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import scrapy
import re

#聚法网裁判文书
class CaipanInfoSpider(scrapy.spiders.Spider):
    name = "jufa"
    allowed_domains = ['www.jufaanli.com']
    start_urls = [
        "http://www.jufaanli.com/search2?TypeKey=1%253A%25E6%25A1%2588"
    ]

    pagesize = 20
    # 爬虫入口爬去所有省下的地址
    def parse(self, response):
         pageurl = 'http://www.jufaanli.com/home/search/searchJson'
         totalPage = (26694941-1) / (self.pagesize+1)
         #totalPage = 2
         for page in range(1,totalPage):
              yield scrapy.FormRequest(url=pageurl,
                                        method="POST",
                                        headers={'X-Requested-With': 'XMLHttpRequest'},
                                        dont_filter=True,
                                        callback=self.parseAjaxList,
                                        errback=self.handle_error,
                                        formdata={"page":str(page),"searchNum":str(self.pagesize)})

    #列表
    def parseAjaxList(self,response):
        data = json.loads(response.body_as_unicode())
        detailUrl='http://www.jufaanli.com/detail/'
        for item in data['info']["searchList"]['list']:
             yield scrapy.Request(url=detailUrl+ item['uuid'],
                               method="GET",
                               dont_filter=True,
                               callback=self.parseAjaxDetail,
                               errback=self.handle_error,
                               )
    #详细
    def parseAjaxDetail(self,response):
         item={}
         #标题
         item['title']= ''.join(response.css('.text-center.text-black::text').re(u'[^指导案例\d号：]'))
         #法院
         item['fanyuan']=''.join(response.xpath(u'//div[@class="col-lg-4 title-area"]/span[text()="审理法院"]/parent::div/following-sibling::div/a/text()').extract())
         #案号
         item['anhao'] = ''.join(response.xpath(u'//div[@class="col-lg-4 title-area"]/span[text()="案号"]/parent::div/following-sibling::div/span/text()').extract())
         #案由
         item['anyou'] = ''.join(response.xpath(u'//div[@class="col-lg-4 title-area"]/span[text()="案由"]/parent::div/following-sibling::div/a/text()').extract())
         #案件类型
         item['type'] = ','.join(response.xpath(u'//div[@class="col-lg-4 title-area"]/span[text()="案件类型"]/parent::div/following-sibling::div/span/text()').extract()).rstrip(',')
         #审判日期
         item['stime'] = ''.join(response.xpath(u'//div[@class="col-lg-4 title-area"]/span[text()="审判日期"]/parent::div/following-sibling::div/span/text()').extract())
         #审理程序
         item['slcx'] = ''.join(response.xpath(u'//div[@class="col-lg-4 title-area"]/span[text()="审理程序"]/parent::div/following-sibling::div/span/text()').extract())
         #关键词
         item['keywords'] = ','.join(response.xpath(u'//div[@class="col-lg-4 title-area"]/span[text()="关键词"]/parent::div/following-sibling::div').css('.info-item.info-item-gray a::text').extract()).rstrip(',')
         #律师and律所
         lvshidic=[];
         for i in response.xpath(u'//div[@class="col-lg-4 title-area"]/span[text()="律师"]/parent::div/following-sibling::div').css('.legislation-info'):
             lvshidic.append({"lvsuo":''.join(i.css('a::text').extract()),'names':''.join(i.css('span::text').extract())})
         item['fagui']=response.css('.eachCiteLaw a::text').extract()
         #律所律师
         item['lvsuolvshi'] =lvshidic
         #内容
         item['content'] = re.sub('(class|name|id)="[^"]*?"','', ''.join(response.xpath('//*[@id="caseText"]').extract()))
         item['collection'] = 'caipan'
         item['source'] = '聚法网'
         item["url"] = response.url
         #item["html"] = response.text
         return item

    def handle_error(self, result, *args, **kw):
        self.logger.error("error url is :%s" % result.request.url)