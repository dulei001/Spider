#!/usr/bin/python
#-*- coding: utf-8 -*-
import scrapy

from lawyer import http_util
from lawyer.items.LawyerInfo_item import LawyerInfoItem


class ShanghaiSpider(scrapy.Spider):
    name = "shanghai_lawyer_spider"
    start_urls = ["http://credit.lawyers.org.cn"]

    def parse(self, response):
        #count =2085
        base_url="http://credit.lawyers.org.cn/lawyer-list.jsp?q=&type=&zoneCode=&businessArea=&page=%s"
        for page in range(1,2085):
            yield scrapy.Request(url=base_url%str(page),
                                  callback=self.parse_list,
                                  errback=self.handle_error)

    def parse_list(self,response):
        detail_domain="http://credit.lawyers.org.cn/"
        detail_path_list=response.xpath('//div[@class="list-base"]/a/@href').extract()
        for detail_path in detail_path_list:
            yield scrapy.Request(url=detail_domain+detail_path,
                                 callback=self.parse_detail,
                                 errback=self.handle_error)

    def parse_detail(self,response):
        item = LawyerInfoItem()
        item["name"]=response.xpath('//div[@class="list-item page"]/dl[@class="user-info"]/dd[@class="name"]/text()').extract_first()
        item["sex"]= 0 if response.xpath('//div[@id="detail01"]/div[@class="body"]/ul[@class="info-list clearfix"]/li[2]/text()').extract_first()==u"男" else 1
        item["nation"]=response.xpath('//div[@id="detail01"]/div[@class="body"]/ul[@class="info-list clearfix"]/li[4]/text()').extract_first()
        item["education"]=response.xpath('//div[@id="detail01"]/div[@class="body"]/ul[@class="info-list clearfix"]/li[5]/text()').extract_first()
        item["political_status"]=response.xpath('//div[@id="detail01"]/div[@class="body"]/ul[@class="info-list clearfix"]/li[7]/text()').extract_first()
        item["headurl"] = ''.join(http_util.downloadImage(response.xpath('//dt[@class="avatar"]/img/@src').extract(), 'lawyer_pics/shanghai'))
        item["lawnumber"]=response.xpath('//div[@id="detail01"]/div[@class="body"]/ul[@class="info-list clearfix"]/li[1]/text()').extract_first()
        item["professional_status"] = 0 if response.xpath('//ul[@class="user-credit"]/li/div/text()').extract_first()==u"正常" else 1
        item["personnel_type"]=response.xpath('//div[@id="detail01"]/div[@class="body"]/ul[@class="info-list clearfix"]/li[6]/text()').extract_first()
        item["start_time"]=response.xpath('//div[@id="detail01"]/div[@class="body"]/ul[@class="info-list clearfix"]/li[9]/text()').extract_first()
        item["get_time"]=response.xpath('//div[@id="detail01"]/div[@class="body"]/ul[@class="info-list clearfix"]/li[10]/text()').extract_first()
        item["cert_type"]=''
        item["profession"]=''
        item["ispartnership"] = ''
        item["firm"] = response.xpath('//dl[@class="user-info"]/dd[@class="info"][2]/a/text()').extract_first()
        item["province"]=u"上海"
        item["url"]=response.url
        item['collection'] = 'lawyers'
        return item

    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)