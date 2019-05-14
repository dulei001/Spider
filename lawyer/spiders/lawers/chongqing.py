#!/usr/bin/python
#-*- coding: utf-8 -*-
import scrapy

from lawyer import http_util
from lawyer.items.LawyerInfo_item import LawyerInfoItem


class ChongQingSpider(scrapy.Spider):
    name = "chongqing_lawyer_spider"
    start_urls = ["http://118.125.243.115/Ntalker/lawyers.aspx"]
    #coun=376
    page_count=376
    curent_page=0

    def parse(self, response):
        if self.curent_page>=self.page_count:
            return []

        send_requests=[]
        self.curent_page = self.curent_page + 1
        formdata = {"Pages":str(self.curent_page),
                    "__VIEWSTATE":response.xpath('//input[@id="__VIEWSTATE"]/@value').extract_first(),
                    "__VIEWSTATEGENERATOR": response.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value').extract_first()}

        send_requests.append(scrapy.FormRequest(url="http://118.125.243.115/Ntalker/lawyers.aspx",
                                     method="POST",
                                     formdata=formdata,
                                     callback=self.parse_list,
                                     errback=self.handle_error))
        return send_requests

    def parse_list(self,response):
        detail_path_list = response.xpath('//p[@class="lawlysonename"]/a/@href').extract()
        send_requests = []

        for detail_path in detail_path_list:
             detail_url="http://118.125.243.115/Ntalker/"+detail_path
             send_requests.append(scrapy.Request(url=detail_url,
                                   callback=self.parse_detail,
                                   errback=self.handle_error))

        send_requests.extend(self.parse(response))
        return send_requests

    def parse_detail(self,response):
        item=LawyerInfoItem()
        item["name"]=response.xpath('//span[@id="Label1"]/text()').extract_first()
        item["sex"] = ''
        item["nation"] =response.xpath('//span[@id="Label6"]/text()').extract_first()
        item["education"] = response.xpath('//span[@id="Label7"]/text()').extract_first()
        item["political_status"] = response.xpath('//span[@id="Label8"]/text()').extract_first()
        headurl= ''.join(response.xpath('//img[@id="Image1"]/@src').extract()).replace('121.197.1.207:8001','118.178.181.229:8000')
        item["headurl"] = ''.join(http_util.downloadImage([headurl],'lawyer_pics/chongqing'))
        item["lawnumber"] = response.xpath('//span[@id="Label11"]/text()').extract_first()
        item["professional_status"] = ''
        item["personnel_type"] = ''
        item["start_time"] =''
        item["get_time"] =response.xpath('//span[@id="Label12"]/text()').extract_first()
        item["cert_type"] = ''
        item["profession"] =''
        item["ispartnership"] = ''
        item["firm"] = response.xpath('//span[@id="Label3"]/text()').extract_first()
        item["province"] = u"重庆"
        item["url"] = response.url
        item['collection'] = 'lawyers'
        return item

    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)


