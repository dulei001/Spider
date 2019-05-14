#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

import pymongo
import scrapy

class CourtAreaSpider(scrapy.spiders.Spider):
    name = "menu_court_area"
    start_urls = [
        "http://wenshu.court.gov.cn/"
    ]
    handle_httpstatus_list = [302]

    def parse(self, response):
        if response.status == 302:
            self.logger.info(u"retry url:"+response.url)
            return response.request

        next = []
        for court_area in self.__get_one_level_court():
            if court_area["name"]==u"最高人民法院":
                court_area["type"] = u"法院层级"
                next.append(court_area)
                continue

            else:
                court_area["type"]=u"法院地域"
                next.append(court_area)

            next.append(scrapy.FormRequest(url="http://wenshu.court.gov.cn/List/CourtTreeContent",
                                     method="POST",
                                     headers={"X-Requested-With": "XMLHttpRequest"},
                                     formdata={"Param": u"法院地域:"+court_area["name"],"parval":court_area["name"]},
                                     callback=self.parse_medium_court,
                                     errback=self.handle_error))
        return next

    def parse_medium_court(self, response):
        if response.status == 302:
            self.logger.info(u"retry url:"+response.url)
            return response.request

        """解析中级法院"""
        next = []
        data=json.loads(response.text.replace("\\","").strip('"'))
        for menu in data:
            child_list = menu["Child"]
            for child in child_list:
                if child["Key"] !="":
                    next.append({"name": child["Key"], "parent": child["parent"], "id": child["id"],"type":u"中级法院"})
                    next.append(scrapy.FormRequest(url="http://wenshu.court.gov.cn/List/CourtTreeContent",
                                             method="POST",
                                             headers={"X-Requested-With": "XMLHttpRequest"},
                                             formdata={"Param": u"中级法院:" + child["Key"],
                                                       "parval": child["Key"],
                                                       "Value":child["Value"]},
                                             callback=self.parse_basis_court,
                                             errback=self.handle_error))
        return next

    def parse_basis_court(self,response):
        """解析基层法院"""
        if response.status == 302:
            self.logger.info(u"retry url:"+response.url)
            return response.request

        data = json.loads(response.text.replace("\\", "").strip('"'))
        for menu in data:
            child_list = menu["Child"]
            for child in child_list:
                if child["Key"] != "":
                    return {"name": child["Key"],
                            "parent": child["parent"],
                            "id": child["id"],
                            "type":"基层法院",
                            "Value": child["Value"]}


    def handle_error(self, result, *args, **kw):
        self.logger.error("error url is :%s" % result.request.url)


    def __get_one_level_court(self):
        client = pymongo.MongoClient(self.settings["MONGO_URI"], replicaSet=self.settings["MONGO_REPLICAT_SET"])
        db= client[self.settings["MONGO_DATABASE"]]
        db.authenticate(self.settings["MONGO_USERNAME"],self.settings["MONGO_PASSWORD"])
        data=db["menu_base"].find_one()
        if data is None:
            return  []

        client.close()
        return data["court_area"]

    # def __insert_court(self,court_area):
    #     client = pymongo.MongoClient(self.settings["MONGO_URI"], replicaSet=self.settings["MONGO_REPLICAT_SET"])
    #     db = client[self.settings["MONGO_DATABASE"]]
    #     db.authenticate(self.settings["MONGO_USERNAME"], self.settings["MONGO_PASSWORD"])
    #     db[self.name].insert_one(court_area)
    #     client.close()
