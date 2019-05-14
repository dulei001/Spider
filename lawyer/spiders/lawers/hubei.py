#!/usr/bin/python
#-*- coding: utf-8 -*-
import scrapy
from lawyer.items.LawyerInfo_item import LawyerInfoItem

#湖北律师抓取
class HuBeiLawyerSpider(scrapy.Spider):
    name = "hubeilawyer_spider"
    allowed_domains = ["hbsf.gov.cn"]
    start_urls = ["http://www.hbsf.gov.cn:8081/application/onlineWeb/lsjjgList"]

    def parse(self, response):
        baseurl='http://www.hbsf.gov.cn:8081/application/onlineWeb/lsjjgList'
        url_items = []
        #总共519页
        for num in range(1, 520):
            detail_request= scrapy.FormRequest(url=baseurl,
                                     method="POST",
                                     callback=self.parseList,
                                     errback=self.handle_error,
                                     formdata={"sortDir": "ASC", "pageNumber": str(num)})
            url_items.append(detail_request)
        return url_items

    def parseList(self,response):
        item = LawyerInfoItem()

        # 地址
        item['url'] = str(response.url)

        for tr in response.xpath('//table/tbody/tr'):
            # 姓名
            item['name'] = "".join(tr.xpath('td[7]/text()').re('[^\s]'))
            # 律师职业证号
            item['lawnumber'] = "".join(tr.xpath('td[8]/text()').re('[^\s]'))
            # 省
            item['province'] = u"湖北"
            # 律所
            item['firm'] = "".join(tr.xpath('td[1]/text()').re('[^\s]'))
            # 性别
            item['sex'] = ''
            # 民族
            item['nation'] = ''
            # 学历
            item['education'] = ''
            # 政治面貌
            item['political_status'] = ''
            # 头像路径
            item['headurl'] = ''
            # 职业状态:0-正常、1-注销
            item['professional_status'] = ''
            # 人员类型:专职
            item['personnel_type'] = ''
            # 首次执业时间
            item['start_time'] = ''
            # 资格证获取时间
            item['get_time'] = ''
            # 证书类型
            item['cert_type'] = ''
            # 专业
            item['profession'] = ''
            # 是否合伙人 0-否 1-是
            item['ispartnership'] = ''
            item['collection'] = 'lawyers'
            yield item


    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)