#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

import math
import scrapy
from pymongo import MongoClient
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TimeoutError, TCPTimedOutError

from devops import scrapyd_cencel
from devops import scrapyd_deploy
from devops import scrapyd_scheduling


class WuSong1949To1990Spider(scrapy.spiders.Spider):
    name = "wusong_1949_1990_spider"
    handle_httpstatus_list = [302]
    years = ["1988"]
    start_url_template="http://www.itslaw.com/search/lawsAndRegulations?searchMode=lawsAndRegulations&sortType=1&conditions=searchWord%2B%E7%9A%84%2B1%2B%E7%9A%84&conditions=publishDate%2B{0}%2B4%2B{1}"
    page_url_template="http://www.itslaw.com/api/v1/lawRegulations?startIndex={0}&countPerPage=20&sortType=1&conditions=searchWord%2B%E7%9A%84%2B1%2B%E7%9A%84&conditions=publishDate%2B{1}%2B4%2B{2}"

    def start_requests(self):
        for year in self.years:
            start_url=self.start_url_template.format(year,year)
            yield scrapy.Request(url=start_url,
                                 method="GET",
                                 callback=self.parse,
                                 meta={"start_url":start_url,"year":year})


    def parse(self, response):
        year=response.meta["year"]
        start_url=response.meta["start_url"]
        return scrapy.Request(url=self.page_url_template.format(str(0), year,year),
                              method="GET",
                              dont_filter=True,
                              meta={"start_url": start_url, "year": year},
                              callback=self.parse_page_count,
                              errback=self.handle_error)

    def parse_page_count(self, response):
         year = response.meta["year"]
         start_url = response.meta["start_url"]
         result=json.loads(response.body_as_unicode())
         count= result["data"]['lawRegulationArticleSearchResult']["publishDateResults"][0]["count"]
         next=[]
         next.extend(self.parse_page_list(response))
         if count>20:
             page_count = math.floor(count / 20)
             for page_index in range(1, int(page_count) + 1):
                 next.append(scrapy.Request(url=self.page_url_template.format(str(page_index*20), year, year),
                                       method="GET",
                                       headers={"Referer":start_url},
                                       dont_filter=True,
                                       callback=self.parse_page_list,
                                       errback=self.handle_error))
         return next

    def parse_page_list(self,response):
         result=json.loads(response.body_as_unicode())
         articles= result["data"]['lawRegulationArticleSearchResult']['lawRegulationArticles']
         next=[]
         for article in articles:
             if self.__existed_doc(article["lawRegulationId"]):
                 continue

             url = "http://www.itslaw.com/api/v1/lawRegulations/lawRegulation?lawAndRegulationId=%s" % article["lawRegulationId"]
             referer="http://www.itslaw.com/search/lawsAndRegulations/lawAndRegulation?lawAndRegulationId=%s"%article["lawRegulationId"]
             next.append(scrapy.Request(url=url,
                            method="GET",
                            headers={"Referer": referer},
                            dont_filter=True,
                            meta={"article":article},
                            callback=self.parse_detail,
                            errback=self.handle_error))
         return next

    def parse_detail(self,response):
        result = json.loads(response.body_as_unicode())
        article= response.meta["article"]
        article["content"]=result["data"]["lawRegulationDetail"]
        article["collection"]="wusong_law"
        return article

    def handle_error(self, failure):
        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:
        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)
        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)
        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)

    def __existed_doc(self, lawAndRegulationId):
        """获取法院地域,获取所有没有子菜单的法院"""
        client = MongoClient(self.settings["MONGO_URI"], replicaSet=self.settings["MONGO_REPLICAT_SET"])
        db = client[self.settings["MONGO_DATABASE"]]
        db.authenticate(self.settings["MONGO_USERNAME"], self.settings["MONGO_PASSWORD"])
        result = db["wusong_law"].count({"lawAndRegulationId": lawAndRegulationId})
        return result > 0


if __name__ == "__main__":
    # 部署整个工程
    #  scrapyd_deploy.deploy()
    # 运行spider
    #  print scrapyd_scheduling.schedule(project="lawyer", spider=WuSong1949To1990Spider.name)
    # 取消运行spder 执行三次
     print scrapyd_cencel.cancel(project="lawyer",job="223a7e60fd7f11e68bb50242c0a80002")
     pass
