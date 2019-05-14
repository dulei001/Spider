#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

from datetime import datetime
import scrapy
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TimeoutError, TCPTimedOutError

from devops import scrapyd_cencel
from devops import scrapyd_deploy
from devops import scrapyd_scheduling


class IprCourtSpider(scrapy.spiders.Spider):
    name = "ipr_court_spider"
    start_urls = [
       "http://ipr.court.gov.cn/"
    ]

    handle_httpstatus_list = [302]

    def parse(self, response):
        if response.status == 302:
            response.request.headers["Referer"] = "http://wenshu.court.gov.cn"
            response.request.dont_filter = True
            self.logger.info("retry redirect url:" + response.url)
            return response.request

        area_selectors=response.xpath("//table[2]/tr/td[3]/table[3]/tr/td[2]/table/tr/td/a")
        next_requests=[]
        for area_selector in area_selectors:
            area_url=area_selector.xpath("@href").extract_first().replace('.', 'http://ipr.court.gov.cn')
            area_name = area_selector.xpath("text()").extract_first()
            next_requests.append(scrapy.Request(url=area_url+"/",
                                                meta={"area":area_name},
                                                dont_filter=True,
                                                callback=self.parse_area,
                                                errback=self.handle_error))
        return next_requests

    def parse_area(self, response):
        more_urls= response.xpath(u"//a[contains(text(),'更多')]/@href").extract()
        more_urls=list(set(more_urls))
        next_requests=[]
        for more_url in more_urls:
            more_url = more_url.replace('./', response.url)
            next_requests.append(scrapy.Request(url=more_url + "/",
                                                dont_filter=True,
                                                meta={"area": response.meta["area"]},
                                                callback=self.parse_page_count,
                                                errback=self.handle_error))
        return next_requests

    def parse_page_count(self, response):
        area=response.meta["area"]
        issue_type=response.xpath("//table[2]/tr/td[3]/table[1]/tr/td[2]/a[3]/text()").extract_first()
        script_count="".join(response.xpath('//script[contains(text(),"createPageHTML")]/text()').extract()).strip()
        count= int(re.findall(r'createPageHTML.(\d+),.*;',script_count)[0])
        next_requests=[]
        for index in range(0,count):
             if index ==0:
                 page_url=response.url+"index.html"
             else:
                 page_url = response.url + "index_"+str(index)+".html"

             next_requests.append(scrapy.Request(url=page_url,
                                                 dont_filter=True,
                                                 meta={"area": response.meta["area"],"issue_type":issue_type,"area_url":response.url},
                                                 callback=self.parse_page,
                                                 errback=self.handle_error))
        return next_requests

    def parse_page(self,response):
        detail_urls_selector=response.xpath("//table[2]/tr/td[3]/table[2]/tr[2]/td/table[1]/tr/td/a")
        for detail_url_selector in detail_urls_selector:
            yield scrapy.Request(url=response.meta["area_url"]+detail_url_selector.xpath("@href").extract_first().lstrip("./"),
                                 meta={"area": response.meta["area"],
                                       "issue_type":response.meta["issue_type"],
                                       "title":detail_url_selector.xpath("text()").extract_first()},
                                 dont_filter=True,
                                 callback=self.parse_detail,
                                 errback=self.handle_error)

    def parse_detail(self,response):
        title = response.meta["title"]
        area = response.meta["area"]
        content = "".join(response.xpath('//*[@id="content"]').extract())
        issue_type=response.meta["issue_type"]

        model = {"createtime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 "collection": "ipr_court",
                 "url": response.url,
                 "title": title,
                 "area": area,
                 "content": content,
                 "issue_type": issue_type
                 }
        try:
            trunk_content="".join(response.xpath('//*[@id="content"]//text()').extract())[0:100].replace(" ","")
            split_content=trunk_content.split(u"（")
            court_content= self.__extract_chinese(split_content[0])
            court=court_content[0:len(court_content)-5]
            judgment_type= court_content[len(court_content)-5:len(court_content)]
            year=re.findall(u"(\d+)）.*",split_content[1])[0]
            case_number_content=split_content[1].replace(u"（","").replace(u"）","").replace(year,"")
            case_number_index= case_number_content.find(u"号")
            case_number=case_number_content[0:case_number_index+1]

            model["judgment_type"]=judgment_type
            model["court"]=court
            model["year"]=year
            model["case_number"]=case_number
        finally:
            return model

    def __extract_chinese(self,str):
        line = str.strip()
        p2 = re.compile(ur'[^\u4e00-\u9fa5]')
        zh = " ".join(p2.split(line)).strip()
        zh = ",".join(zh.split())
        outStr = zh  # 经过相关处理后得到中文的文本
        return outStr

    def handle_error(self, failure):
            self.logger.error(repr(failure))
            if failure.check(HttpError):
                response = failure.value.response
                self.logger.error('HttpError on %s', response.url)
            elif failure.check(DNSLookupError):
                # this is the original request
                request = failure.request
                self.logger.error('DNSLookupError on %s', request.url)
            elif failure.check(TimeoutError, TCPTimedOutError):
                request = failure.request
                self.logger.error('TimeoutError on %s', request.url)


if __name__ == "__main__":
    # 部署整个工程
       scrapyd_deploy.deploy()
    # 运行spider
       print scrapyd_scheduling.schedule(project="lawyer", spider=IprCourtSpider.name)
    # 取消运行spder 执行三次
    #  print scrapyd_cencel.cancel(project="lawyer",job="2ff68c9a022c11e78bb50242c0a80002")

