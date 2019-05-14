#!/usr/bin/python
#-*- coding: utf-8 -*-

import scrapy

from lawyer import http_util
from lawyer.items.LawyerInfo_item import LawyerInfoItem
class ShangXiSpider(scrapy.Spider):
    name = "shangxi_spider"
    allowed_domains = ['sx.sxlawyer.cn']
    start_urls = ["http://sx.sxlawyer.cn"]

    def parse(self, response):
        baseurl = "http://sx.sxlawyer.cn/lvshiS.aspx"
        url_items = []
        # 总页数484
        for num in range(1, 485):
            url_list = 'http://sx.sxlawyer.cn/lvshiS.aspx?page='+str(num)
            yield scrapy.Request(url=url_list,
                                 method='GET',
                                 dont_filter=True,
                                 callback=self.pase_item,
                                 errback=self.handle_error)

    def pase_item(self, response):
        item_urls = response.xpath('//table[@class="danga"]/tr/td[1]/a/@href').extract()
        for item_url in item_urls:
            yield scrapy.Request(url='http://sx.sxlawyer.cn' + item_url, callback=self.pase_item_details)

    def pase_item_details(self, response):
        detail_item=  LawyerInfoItem()
        detail_item["url"] = response.url
        #省份
        detail_item["province"]=u"山西"
        #姓名
        detail_item["name"]="".join(response.xpath('//*[@id="Form1"]/div[3]/div[2]/table/tr[1]/td[2]/text()').extract())
        #性别
        sex = "".join(response.xpath('//*[@id="Form1"]/div[3]/div[2]/table/tr[1]/td[4]/text()').extract())
        if(sex==u"男"):
            detail_item["sex"]="0"
        elif(sex==u"女"):
            detail_item["sex"]="1"
        else:
            detail_item["sex"]=""
        #民族
        detail_item["nation"]="".join(response.xpath('//*[@id="Form1"]/div[3]/div[2]/table/tr[2]/td[2]/text()').extract())
       #学历
        detail_item["education"] = "".join(response.xpath('//*[@id="Form1"]/div[3]/div[2]/table/tr[2]/td[4]/text()').extract())
        # 政治面貌
        detail_item["political_status"] = "".join(response.xpath('//*[@id="Form1"]/div[3]/div[2]/table/tr[3]/td[4]/text()').extract())
        # 头像路径
        headurl = "".join(response.xpath('//*[@id="Form1"]/div[3]/div[2]/table/tr[1]/td[5]/img/@src').extract())
        if(headurl==""):
            detail_item["headurl"] = ""
        else:
            detail_item["headurl"] = ''.join(http_util.downloadImage(["http://sx.sxlawyer.cn".join(response.xpath('//*[@id="Form1"]/div[3]/div[2]/table/tr[1]/td[5]/img/@src').extract())], 'lawyer_pics/shanxi'))
        # 律师职业证号
        detail_item["lawnumber"] = "".join(response.xpath('//*[@id="Form1"]/div[3]/div[2]/table/tr[6]/td[4]/text()').extract())
        # 职业状态:0-正常、1-注销
        professional_status ="".join(response.xpath('//*[@id="Form1"]/div[3]/div[2]/table/tr[7]/td[2]/text()').extract())
        if(professional_status==u"在职"):
            detail_item["professional_status"] ="0"
        else:
            detail_item["professional_status"] = "1"
        # 人员类型:专职
        detail_item["personnel_type"] = "".join(response.xpath('//*[@id="Form1"]/div[3]/div[2]/table/tr[6]/td[2]/text()').extract())
        # 首次执业时间
        detail_item["start_time"] = "".join(response.xpath('//*[@id="Form1"]/div[3]/div[2]/table/tr[10]/td[2]/text()').extract())
        # 资格证获取时间
        detail_item["get_time"] = "".join(response.xpath('//*[@id="Form1"]/div[3]/div[2]/table/tr[8]/td[2]/text()').extract())
        # 证书类型
        detail_item["cert_type"] = ""
        # 专业
        detail_item["profession"] = ""
        # 是否合伙人 0-否 1-是
        ispartnership="".join(response.xpath('//*[@id="Form1"]/div[3]/div[2]/table/tr[2]/td[1]/text()').extract())
        if(ispartnership==u"是"):
             detail_item["ispartnership"] ="1"
        elif(ispartnership==u"否"):
            detail_item["ispartnership"]="0"
        else:
            detail_item["ispartnership"]=""
        # 所属律所
        detail_item["firm"] = "".join(response.xpath('//*[@id="Form1"]/div[3]/div[2]/table/tr[8]/td[4]/text()').extract())
        detail_item['collection'] = 'lawyers'
        return detail_item

    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)

