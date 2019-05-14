#!/usr/bin/python
#-*- coding: utf-8 -*-
import scrapy
from lawyer.items.LawyerInfo_item import LawyerInfoItem

#河南律师抓取
class HNLawyerSpider(scrapy.Spider):
    name = "hnlawyer_spider"
    allowed_domains = ["hnlawyer.org"]
    start_urls = ["http://www.hnlawyer.org/index.php/index-lawyercx"]

    def parse(self, response):
        #总共677页
        for p in range(1, 678):
            url = 'http://www.hnlawyer.org/index.php/Home-index-lawyercx-is_check-1-is_check-1-p-%d'%p
            yield scrapy.Request(url,method = 'GET',callback=self.parseList,errback=self.handle_error)


    def parseList(self,response):
        item = LawyerInfoItem()

        # 地址
        item['url'] = str(response.url)

        for tr in response.xpath('//table[@class="tab_list"]/tr[@bgcolor="#f0f0f0"]'):
            # 姓名
            item['name'] = "".join(tr.xpath('td[1]/a/text()').re('[^\s]'))
            # 律师职业证号
            item['lawnumber'] = "".join(tr.xpath('td[2]/text()').re('[^\s]'))
            # 省
            item['province'] = u"河南"
            # 律所
            item['firm'] = "".join(tr.xpath('td[4]/text()').re('[^\s]'))
            #性别
            item['sex']=''
            # 民族
            item['nation']=''
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
            item['cert_type']=''
            # 专业
            item['profession'] = ''
            # 是否合伙人 0-否 1-是
            item['ispartnership'] = ''
            item['collection'] = 'lawyers'
            yield item


    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)