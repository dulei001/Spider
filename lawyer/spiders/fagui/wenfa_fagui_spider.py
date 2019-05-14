#!/usr/bin/python
#-*- coding: utf-8 -*-
import re
import uuid
from datetime import datetime
import scrapy

from dal.service.StatuteData import StatuteData


class WFFGSpider(scrapy.Spider):
    """问法法律法规"""

    name = "wffagui_NoFilter"

    allowed_domains=["www.51wf.com"]

    last_faguis=[
                    {'source':u'部门规章', 'pubish_time':'2018-04-27'},#部门规章
                    #{'source':u'行政法规', 'pubish_time':'2012-11-12'},
                 ]
    statuteData = StatuteData()
    start_urls = [
        "http://www.51wf.com/law/search--authority-1--page-1", #宪法
        "http://www.51wf.com/law/search--authority-2--page-1",  # 行政行规
        "http://www.51wf.com/law/search--authority-3--page-1",  # 司法解释
        "http://www.51wf.com/law/search--authority-4--page-1",  # 部门规章
        "http://www.51wf.com/law/search--authority-5--page-1",  # 军事专项法
        "http://www.51wf.com/law/search--authority-6--page-1",  # 行政团体规定
        "http://www.51wf.com/law/search--authority-7--page-1",  # 地方法规规章
        ]

    def parse(self, response):
       self.parse_list(response)
       page_count=''.join(response.xpath("//a[@name='last']/text()").extract())
       if page_count=="":
           return ;
       data_total= int(page_count)
       pageurl=str(response.url)[0:len(response.url)-1]
       for page in range(2, data_total):
         yield scrapy.Request(pageurl+str(page) ,callback=self.parse_list,method='get',errback=self.handle_error)

    def parse_list(self,response):
         domain="http://www.51wf.com%s"
         for item in response.css(".lie_biao li"):
             detail_url=domain % item.css(".xin_wen a::attr(href)").extract_first()
             #if datetime.strptime(self.last_faguis[0]['pubish_time'], "%Y-%m-%d") < datetime.strptime(item.css(".shi_jian span::text").extract_first(), "%Y-%m-%d"):
             yield scrapy.Request(detail_url, callback=self.parse_detail, method='get',
                                          errback=self.handle_error)




    def parse_detail(self,response):
        item = {}
        item['title'] = "".join(response.css('.LL_bt_a::text').re('[^\s]'))
        # 发文字号
        item['anNo'] = "".join(response.xpath(u'//div[@class="LL_sx"]/p[contains(text(),"【发文字号】")]/text()').re('[^\s]')).replace(u'【发文字号】','')
        # 颁布日期
        item['pubish_time'] = "".join(response.xpath(u'//div[@class="LL_sx"]/p[contains(text(),"【颁布日期】")]/text()').re('[^\s]')).replace(u'【颁布日期】','')
        # 时效性
        if len( response.xpath(u'//div[@class="LL_sx"]/p[contains(text(),"【时效性】")]'))>1:
            item['time_liness'] = "".join(
                response.xpath(u'//div[@class="LL_sx"]/p[contains(text(),"【时效性】")][2]/text()').re('[^\s]')).replace(
                u'【时效性】', '')
        else:
            item['time_liness'] ="".join(response.xpath(u'//div[@class="LL_sx"]/p[contains(text(),"【时效性】")][1]/text()').re('[^\s]')).replace(u'【时效性】','')
        # 生效日期
        item['effect_time'] = "".join(response.xpath(u'//div[@class="LL_sx"]/p[contains(text(),"【生效日期】")]/text()').re('[^\s]')).replace(u'【生效日期】','')
        # 效力级别
        item['level'] = "".join(response.xpath(u'//div[@class="LL_sx"]/p[contains(text(),"【效力级别】")]/span/a/text()').re('[^\s]'))
        # 颁布机构
        item['pubish_org'] = "".join(response.xpath(u'//div[@class="LL_sx"]/p[contains(text(),"【颁布机构】")]/text()').re('[^\s]')).replace(u'【颁布机构】','')
        #[@class!="law_realate"]
        content = ''.join(response.css('.law-content').extract())

        #替换【相关资料】【相关词条】 等内容
        for cxt in  response.css('.law_realate').extract():
            content = content.replace(cxt,"")

        item["content"] = re.sub('(class|style|color|href|name)="[^"]*?"', '', content)  # 内容
        item['url'] = response.url
        item['source'] = u"问法法规"
        uid = str(uuid.uuid1()).replace('-', '')
        self.statuteData.insert_statute((uid, item['time_liness'], item['effect_time'], item['level'], item['pubish_time'],
                                       item['title'], item['anNo'], item['source'], item['pubish_org'],
                                       item["content"], 0))
        del item["content"]
        print item



    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)
