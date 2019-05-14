#!/usr/bin/python
#-*- coding: utf-8 -*-
import scrapy

from lawyer import http_util
from lawyer.items.LawyerInfo_item import LawyerInfoItem


class ShanXiLawerSpider(scrapy.Spider):
    """ 陕西律师抓取"""
    name = "shanxi_lawer_spider"
    start_urls = ["http://www.sxsf.gov.cn/public/WwAjaxAction/SetPath?url=/public/sxsfww/ggflfw/bsfw/listlsjg&queryCs=lssws&queryUl=lsul"]

    def parse(self, response):
        for index in range(1,307):
            yield scrapy.FormRequest(url="http://www.sxsf.gov.cn/public/sxsfww/ggflfw/bsfw/listlsxx",
                                 method="POST",
                                 formdata={"countSize":str(index*20),
                                           "startSize":str((index-1)*20+1),
                                           "countPage":str(26),
                                           "pagedw":str(1),
                                           "doAction":"",
                                           "sys_menuid":"",
                                           "xm":"",
                                           "xb": "",
                                           "kz20": "",
                                           "szdq": "",
                                           "lsjgbh": ""
                                           },
                                 callback=self.parse_page,
                                 errback=self.handle_error)

    def parse_page(self,response):
        detail_urls=response.xpath("//table/tr/td/a/@href").extract()
        for detail_url in detail_urls:
            yield scrapy.Request(url="http://www.sxsf.gov.cn"+detail_url,
                                     method="GET",
                                     callback=self.parse_detail,
                                     errback=self.handle_error)

    def parse_detail(self,response):
        item = LawyerInfoItem()
        item["name"]=response.xpath("//table/tr[1]/td[1]/text()").extract_first()
        sex=response.xpath("//table/tr[1]/td[2]/text()").extract_first()
        if sex is not  None:
            sex=sex.strip()
        if sex==u"男":
            sex=0
        elif sex==u"女":
            sex=1
        else:
            sex=""
        item["sex"] =sex
        item["education"]=response.xpath("//table/tr[5]/td[2]/text()").extract_first()
        item["political_status"]=response.xpath("//table/tr[2]/td[2]/text()").extract_first()
        headurl='http://www.sxsf.gov.cn'+response.xpath('//table/tr[1]/td[3]/img/@src').extract_first()
        item["headurl"] = ''.join(http_util.downloadImage([headurl], 'lawyer_pics/sshanxi'))
        item["lawnumber"] = response.xpath("//table/tr[3]/td[1]/text()").extract_first()
        item["get_time"] = response.xpath("//table/tr[4]/td[1]/text()").extract_first()
        item["cert_type"] = response.xpath("//table/tr[3]/td[2]/text()").extract_first()
        item["profession"] = ''.join(response.xpath("//table/tr[9]/td[1]/text()").extract()).split(u'、')
        item["firm"] = response.xpath("//table/tr[10]/td[1]/a/text()").extract_first()
        item['collection'] = 'lawyers'
        item['province']=u'陕西'
        item['url'] = response.url
        return item

    def handle_error(self, result, *args, **kw):
        self.logger.error("error url is :%s" % result.request.url)

