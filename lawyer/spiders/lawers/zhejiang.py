#!/usr/bin/python
#-*- coding: utf-8 -*-
import scrapy
from lawyer.items.LawyerInfo_item import LawyerInfoItem

class ZheJiangSpider(scrapy.Spider):
    name = "zhejiang_spider"
    #allowed_domains = ['www.fjsf.gov.cn']
    start_urls = ["http://220.191.244.19/zjlawyermanager/view/lawyers/LawyerPageList/execute/lawyersList.do"]

    def parse(self, response):
        #总页数1158
        for num in range(1, 1158, 1):
            yield scrapy.FormRequest(url='http://220.191.244.19/zjlawyermanager/view/lawyers/LawyerPageList/execute/lawyersList.do',
                                     method="POST",
                                     callback=self.pase_item,
                                     errback=self.handle_error,
                                     formdata={"pageNo": str(num)})

    def pase_item(self,response):
         item_urls= response.xpath('//table[4]/tr/td[1]/table/tr/td[2]/table[3]/tr[1]/td[2]/table[2]/tr/td[1]/a/@href').extract()
         for item_url in item_urls:
            yield  scrapy.Request(url='http://220.191.244.19/'+item_url,callback=self.pase_item_details)

    def pase_item_details(self,response):
        detail_item = LawyerInfoItem()
        #页面url
        detail_item["url"] = response.url
        # 省份
        detail_item["province"] = "浙江"
        # 姓名
        detail_item["name"] = "".join( response.xpath('//table[4]/tr/td[1]/table/tr/td[2]/table[3]/tr[1]/td[2]/text()').extract())
        # 性别
        sex = "".join(response.xpath('//table[4]//tr/td[1]/table/tr/td[2]/table[3]/tr[4]/td[2]/text()').extract())
        if (sex == u"男"):
            detail_item["sex"] = "0"
        elif (sex == u"女"):
            detail_item["sex"] = "1"
        else:
            detail_item["sex"] = ""

        # 民族
        detail_item["nation"] = ""
        # 学历
        detail_item["education"] = ""
        # 政治面貌
        detail_item["political_status"] = ""
        # 头像路径
        detail_item["headurl"] = ""
        # 律师职业证号
        detail_item["lawnumber"] = "".join(response.xpath('//table[4]/tr/td[1]/table/tr/td[2]/table[3]/tr[7]/td[2]/text()').extract())
        # 职业状态:0-正常、1-注销
        detail_item["professional_status"] = ""
        # 人员类型:专职
        detail_item["personnel_type"] = "".join(response.xpath('/html/body/table[4]/tbody/tr/td[1]/table/tbody/tr/td[2]/table[3]/tbody/tr[6]/td[2]/text()').extract())
        # 首次执业时间
        detail_item["start_time"] = ""
        # 资格证获取时间
        detail_item["get_time"] = ""
        # 证书类型
        detail_item["cert_type"] = ""
        # 专业
        detail_item["profession"] = ''
        # 是否合伙人 0-否 1-是
        detail_item["ispartnership"] = ""
        # 所属律所
        detail_item["firm"] = "".join(response.xpath('//table[4]/tr/td[1]/table/tr/td[2]/table[3]/tr[2]/td[2]/a/text()').extract())
        detail_item['collection'] = 'lawyers'
        return detail_item

    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)