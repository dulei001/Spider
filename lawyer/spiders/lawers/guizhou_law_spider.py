#!/usr/bin/python
#-*- coding: utf-8 -*-
import scrapy
from lawyer.items.LawyerInfo_item import LawyerInfoItem

class GuiZhouSpider(scrapy.Spider):
    name = "guizhou_spider"
    #allowed_domains = ['www.fjsf.gov.cn']
    start_urls = ["http://www.gysf.gov.cn/bmpd/list_infor_lscx.aspx?xid=&xm=&xb=&lssws=&zyzh=&pg=0"]

    def parse(self, response):
        self.pase_item(response)
        for num in range(1, 100):
            yield scrapy.Request(url='http://www.gysf.gov.cn/bmpd/list_infor_lscx.aspx?xid=&xm=&xb=&lssws=&zyzh=&pg=%s' % str(num),
                                     method="get",
                                     callback=self.pase_item,
                                     errback=self.handle_error
                                     )

    def pase_item(self,response):
         item_urls= response.xpath('//table[@class="tableLb"]/tr[position()>1]/td[1]/a/@href').extract()
         for item_url in item_urls:
            yield  scrapy.Request(url='http://www.gysf.gov.cn'+item_url,callback=self.pase_item_details)

    def pase_item_details(self,response):
        detail_item = LawyerInfoItem()
        #页面url
        detail_item["url"] = response.url
        # 省份
        detail_item["province"] = u"贵州"
        # 姓名
        detail_item["name"] = "".join(response.xpath('//*[@id="form1"]/center/div/div[3]/div[2]/div[2]/table/tr[1]/td/table/tr[1]/td[3]/text()').re('[^\s+]'))
        # 性别
        sex = "".join(response.xpath('//*[@id="form1"]/center/div/div[3]/div[2]/div[2]/table/tr[1]/td/table/tr[2]/td[2]/text()').re('[^\s+]'))
        if (sex == u"男"):
            detail_item["sex"] = "0"
        elif (sex == u"女"):
            detail_item["sex"] = "1"
        else:
            detail_item["sex"] = ""
        # 民族
        detail_item["nation"] = "".join(response.xpath('//*[@id="form1"]/center/div/div[3]/div[2]/div[2]/table/tr[1]/td/table/tr[2]/td[4]/text()').re('[^\s+]'))
        # 学历
        detail_item["education"] = "".join(response.xpath('//*[@id="form1"]/center/div/div[3]/div[2]/div[2]/table/tr[1]/td/table/tr[6]/td[2]/text()').re('[^\s+]'))
        # 政治面貌
        detail_item["political_status"] = "".join(response.xpath('//*[@id="form1"]/center/div/div[3]/div[2]/div[2]/table/tr[1]/td/table/tr[3]/td[2]/text()').re('[^\s+]'))
        # 头像路径
        detail_item["headurl"] = ""
        # 律师职业证号
        detail_item["lawnumber"] = "".join(response.xpath('//*[@id="form1"]/center/div/div[3]/div[2]/div[2]/table/tr[1]/td/table/tr[4]/td[2]/text()').re('[^\s+]'))
        # 职业状态:0-正常、1-注销
        detail_item["professional_status"] = ""
        # 人员类型:专职
        detail_item["personnel_type"] = "".join(response.xpath('/html/body/table[4]/tr/td[1]/table/tr/td[2]/table[3]/tr[6]/td[2]/text()').re('[^\s+]'))
        # 首次执业时间
        detail_item["start_time"] ="".join(response.xpath('//*[@id="form1"]/center/div/div[3]/div[2]/div[2]/table/tr[1]/td/table/tr[8]/td[2]/text()').re('[^\s+]'))
        # 资格证获取时间
        detail_item["get_time"] = "".join(response.xpath('//*[@id="form1"]/center/div/div[3]/div[2]/div[2]/table/tr[1]/td/table/tr[5]/td[4]/text()').re('[^\s+]'))
        # 证书类型
        detail_item["cert_type"] = ""
        # 专业
        detail_item["profession"] = ''
        # 是否合伙人 0-否 1-是
        detail_item["ispartnership"] = ""
        # 所属律所
        detail_item["firm"] = "".join(response.xpath('//*[@id="form1"]/center/div/div[3]/div[2]/div[2]/table/tr[1]/td/table/tr[3]/td[4]/a/text()').re('[^\s+]'))
        detail_item['collection'] = 'lawyers'
        return detail_item

    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)