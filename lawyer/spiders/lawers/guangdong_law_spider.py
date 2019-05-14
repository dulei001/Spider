#!/usr/bin/python
#-*- coding: utf-8 -*-

import scrapy
from lawyer.items.LawyerInfo_item import LawyerInfoItem
class GuangDongSpider(scrapy.Spider):
    name = "guangdong_spider"
    start_urls = ["http://www.gdlawyer.gov.cn:91/websuite/query/lawyerInfo.jsp?personCode=1"]

    def parse(self, response):
        self.parse(response)
        for num in range(2, 200001):
            url_detail = 'http://www.gdlawyer.gov.cn:91/websuite/query/lawyerInfo.jsp?personCode='+str(num)
            yield scrapy.Request(url=url_detail,
                                 method='GET',
                                 dont_filter=True,
                                 callback=self.pase_item_details,
                                 errback=self.handle_error)


    def pase_item_details(self, response):
        if response.status == 200:
            detail_item = LawyerInfoItem()
            detail_item["url"] = response.url
            #省份
            detail_item["province"]=u"广东"
            #姓名
            detail_item["name"]="".join(response.xpath('//input[@name="textfield22"]/@value').extract())
            #性别
            sex = "".join(response.xpath('//input[@name="textfield224"]/@value').extract())
            if(sex==u"男"):
                detail_item["sex"]="0"
            elif(sex==u"女"):
                detail_item["sex"]="1"
            else:
                detail_item["sex"]=""
            #民族
            detail_item["nation"]="".join(response.xpath('//input[@name="textfield222"]/@value').extract())
            #学历
            detail_item["education"] = "".join(response.xpath('//input[@name="textfield225"]/@value').extract())
            # 政治面貌
            detail_item["political_status"] = ""
            # 头像路径
            detail_item["headurl"] = ""
            # 律师职业证号
            detail_item["lawnumber"] = "".join(response.xpath('//input[@name="textfield223"]/@value').extract())
            # 职业状态:0-正常、1-注销
            professional_status ="".join(response.xpath('//input[@name="textfield529"]/@value').extract())
            if(professional_status==u"正常"):
                detail_item["professional_status"] ="0"
            else:
                detail_item["professional_status"] = "1"
            # 人员类型:专职
            detail_item["personnel_type"] = ""
            # 首次执业时间
            detail_item["start_time"] = ''
            # 资格证获取时间
            detail_item["get_time"] = "".join(response.xpath('//input[@name="textfield227"][1]/@value').extract())
            # 证书类型
            detail_item["cert_type"] = ""
            # 专业
            detail_item["profession"] = ""
            # 是否合伙人 0-否 1-是
            detail_item["ispartnership"]=""
            # 所属律所
            detail_item["firm"] = "".join(response.xpath('//input[@name="textfield229"]/@value').extract())
            detail_item['collection'] = 'lawyers'
            return detail_item

    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)

