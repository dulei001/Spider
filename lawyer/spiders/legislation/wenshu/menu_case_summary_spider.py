#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

import pymongo
import scrapy

class SummarySpider(scrapy.spiders.Spider):
    name = "menu_case_summary"
    start_urls = [
        "http://wenshu.court.gov.cn/"
    ]
    handle_httpstatus_list = [302]

    def parse(self, response):
        if response.status == 302:
            self.logger.info(u"retry url:"+response.url)
            return response.request

        next=[]
        for case_summary in self.__get_all_one_level_case():
            case_summary["type"] = u"一级案由"
            next.append(case_summary)
            next.append(scrapy.FormRequest(url="http://wenshu.court.gov.cn/List/ReasonTreeContent",
                                     method="POST",
                                     headers={"X-Requested-With": "XMLHttpRequest"},
                                     formdata={"Param": u"一级案由:" + case_summary["name"], "parval": case_summary["name"]},
                                     callback=self.parse_two_level_case_summary,
                                     errback=self.handle_error))
        return next
        pass

    def parse_two_level_case_summary(self,response):
        if response.status == 302:
            self.logger.info(u"retry url:"+response.url)
            return response.request

        data = json.loads(response.text.replace("\\", "").strip('"'))
        next = []
        for menu in data:
            child_list = menu["Child"]
            for child in child_list:
                if child["Key"] != "":
                    next.append({"name": child["Key"], "parent": child["parent"], "id": child["id"],"type":u"二级案由","value":child["Value"]})
                    next.append(scrapy.FormRequest(url="http://wenshu.court.gov.cn/List/ReasonTreeContent",
                                             method="POST",
                                             headers={"X-Requested-With": "XMLHttpRequest"},
                                             formdata={"Param": u"二级案由:" + child["Key"],
                                                       "parval": child["Key"]},
                                             callback=self.parse_three_level_case_summary,
                                             errback=self.handle_error))
        return next

    def parse_three_level_case_summary(self, response):
        if response.status == 302:
            self.logger.info(u"retry url:"+response.url)
            return response.request

        data = json.loads(response.text.replace("\\", "").strip('"'))
        next = []
        for menu in data:
            child_list = menu["Child"]
            for child in child_list:
                if child["Key"] != "":
                    next.append({"name": child["Key"], "parent": child["parent"], "id": child["id"],"type":u"三级案由","value":child["Value"]})
                    next.append(scrapy.FormRequest(url="http://wenshu.court.gov.cn/List/ReasonTreeContent",
                                             method="POST",
                                             headers={"X-Requested-With": "XMLHttpRequest"},
                                             formdata={"Param": u"三级案由:" + child["Key"],
                                                       "parval": child["Key"]},
                                             callback=self.parse_four_level_case_summary,
                                             errback=self.handle_error))
        return next

    def parse_four_level_case_summary(self, response):
        if response.status == 302:
            self.logger.info(u"retry url:"+response.url)
            return response.request

        data = json.loads(response.text.replace("\\", "").strip('"'))
        next=[]
        for menu in data:
            child_list = menu["Child"]
            for child in child_list:
                if child["Key"] != "":
                    next.append({"name": child["Key"], "parent": child["parent"], "id": child["id"],"type":u"四级案由","value":child["Value"]})
        return next

    def handle_error(self, result, *args, **kw):
        self.logger.error("error url is :%s" % result.request.url)

    def __get_all_one_level_case(self):
        client = pymongo.MongoClient(self.settings["MONGO_URI"], replicaSet=self.settings["MONGO_REPLICAT_SET"])
        db = client[self.settings["MONGO_DATABASE"]]
        db.authenticate(self.settings["MONGO_USERNAME"], self.settings["MONGO_PASSWORD"])
        data = db["menu_base"].find_one()
        if data is None:
            return []

        client.close()
        return data["one_level_case"]

    # def __insert_case_summary(self, case_summary):
    #     client = pymongo.MongoClient(self.settings["MONGO_URI"], replicaSet=self.settings["MONGO_REPLICAT_SET"])
    #     db = client[self.settings["MONGO_DATABASE"]]
    #     db.authenticate(self.settings["MONGO_USERNAME"], self.settings["MONGO_PASSWORD"])
    #     db[self.name].insert_one(case_summary)
    #     client.close()