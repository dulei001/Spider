#!/usr/bin/python
#-*- coding: utf-8 -*-
import json
import scrapy
from scrapy import Selector


class LegalminerSpider(scrapy.spiders.Spider):
    """理脉裁判文书抓取"""

    name = "legalminer_spider"
    start_urls = [
        "http://www.legalminer.com/"
    ]

    def parse(self, response):
        # return scrapy.Request(url="http://www.legalminer.com/cases?id=5854592f54d07a13c017741c&t=%E7%9A%84%7C",
        #                           dont_filter=True,
        #                           callback=self.parse_detail,
        #                           errback=self.handle_error)
        return scrapy.Request(url="http://www.legalminer.com/search/cases?t=%E7%9A%84&status=false&userId=",
                                  dont_filter=True,
                                  callback=self.parse_base_curt_list,
                                  errback=self.handle_error)

    def parse_base_curt_list(self, response):
        base_curt_list=response.xpath('//div[@class="filtervalue"][3]/ul[@class="list"]/li[4]/ul/li/@data-list-value').extract()
        for base_curt in base_curt_list:
            url=u"http://www.legalminer.com/search/cases?"
            url+=u"court="+u"AND%24{0}%24{1}".format(base_curt,base_curt)
            url+=u"&t=AND%24的&status=false&userId="
            yield scrapy.Request(url=url,
                              dont_filter=True,
                              meta={"court": base_curt},
                              callback=self.parse_year,
                              errback=self.handle_error)

    def parse_year(self,response):
        years = response.xpath(
            '//div[@data-list-value="year"]/ul/li/@data-list-value').extract()
        court=response.meta["court"]
        for year in years:
            yield scrapy.Request(url=u"http://www.legalminer.com/search/cases?court=AND%24{0}%24{1}&t=AND%24的&year=AND%24{2}%24{3}&status=true&userId="
                                 .format(court,court,year,year),
                                 dont_filter=True,
                                 meta={"court":court,"year": year},
                                 callback=self.parse_count,
                                 errback=self.handle_error)

    def parse_count(self,response):
        court = response.meta["court"]
        year = response.meta["year"]
        title=response.xpath('//div[@class="title mb30"]/text()').extract_first()
        count=int(title.strip().replace(u"搜索共找到 ","").replace(u" 份裁判文书",""))
        page =count/10
        for page_index in range(1,page+1):
            yield scrapy.Request(url=u"http://www.legalminer.com/ajax_search/get_html?court=AND%24{0}%24{1}&t=AND%24的&year=AND%24{2}%24{3}&status=true&userId=&page={4}&searchType=cases&sortField=&UserId=&sortType=DESC"
                                 .format(court,court,year,year,str(page_index)),
                                 headers={"X-Requested-With":"XMLHttpRequest"},
                                 callback=self.parse_page,
                                 errback=self.handle_error)


    def parse_page(self,response):
        data = json.loads(response.body_as_unicode())
        html=u"".join(data["result"]["html"])
        id_list=Selector(text=html).xpath("//li/@data-id").extract()
        for id in id_list:
            yield scrapy.Request(
                url=u"http://www.legalminer.com/cases?id={0}&t=的%7C"
                .format(id),
                callback=self.parse_detail,
                errback=self.handle_error)
        pass

    def parse_detail(self,response):
        title= "".join(response.xpath('//div[@class="title fontc6 mb10"]/text()').extract())
        court = "".join(response.xpath('//div[@class="font13 fontc1 mb5"][1]/span[1]/text()').extract())
        case_number = "".join(response.xpath('//div[@class="font13 fontc1 mb5"][1]/span[3]/text()').extract())
        judgment_time= "".join(response.xpath('//div[@class="font13 fontc1 mb5"][1]/span[5]/text()').extract()).replace("/","-")
        case_reason= "".join(response.xpath('//div[@class="font13 fontc1 mb5"][2]/span[1]/text()').extract()).replace(u"案由：","").strip()
        content="".join(response.xpath('//div[@id="content"]').extract())
        return {"title":title,
                "court":court,
                "case_number":case_number,
                "judgment_time":judgment_time,
                "case_reason":case_reason,
                "content":content,
                "url":response.url}

    def handle_error(self, result, *args, **kw):
        self.logger.error("error url is :%s" % result.request.url)