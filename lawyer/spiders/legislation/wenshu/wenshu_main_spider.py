#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from datetime import datetime
import scrapy
from pymongo import MongoClient


class WenShuMainSpider(scrapy.spiders.Spider):
    name = "wenshu_main_spider"
    start_urls = [
        "http://wenshu.court.gov.cn/list/list/?sorttype=1"
    ]
    handle_httpstatus_list = [302]

    def parse(self, response):

       if response.status ==302:
           response.request.headers["Referer"] = "http://wenshu.court.gov.cn"
           self.logger.info("retry redirect url:"+response.url)
           response.request.dont_filter = True
           return response.request

       send_requests=[]
       print len(self.__get_wenshu_all_type())
       print len(self.__get_judgement_program())
       print len(self.__get_judgement_years())
       print len(self.__get_court_area())
       print len(self.__get_case_summary())
       # for wenshu_type in self.__get_wenshu_all_type():
       #     for judgement_program in self.__get_judgement_program():
       #         for judgement_year in self.__get_judgement_years():
       #             for court_area in self.__get_court_area():
       #                 for case_summary in self.__get_case_summary():
       #                      for index in range(1,101):
       #                          param = self.__build_param(wenshu_type,judgement_program,judgement_year,court_area,case_summary)
       #                          send_requests.append(scrapy.FormRequest(url="http://wenshu.court.gov.cn/List/ListContent",
       #                                                                  method="POST",
       #                                                                  headers={"X-Requested-With": "XMLHttpRequest"},
       #                                                                  formdata={"Param": param,"Index":str(index),"Page":"20","Order":u"法院层级","Direction":"asc"},
       #                                                                  callback=self.parse_page,
       #                                                                  errback=self.handle_error))
       return send_requests

    def __build_param(self,wenshu_type,judgement_program,judgement_year,court_area,case_summary):
        param=[]
        if wenshu_type is not None:
            param.append(u"文书类型:"+wenshu_type)
        if wenshu_type is not None:
            param.append(u"审判程序:"+judgement_program)
        if wenshu_type is not None:
            param.append(u"裁判年份:"+judgement_year)
        if wenshu_type is not None:
            param.append(court_area["type"] + court_area["name"])
        if wenshu_type is not None:
            param.append(case_summary["type"] + case_summary["name"])
        return ",".join(param)

    def parse_page(self,response):
        if response.status == 302:
            self.logger.info("retry redirect url:" + response.url)
            response.request.headers["Referer"] = "http://wenshu.court.gov.cn"
            response.request.dont_filter = True
            return response.request

        try:
            data_list=json.loads(response.text.replace("\\","").strip('"'))
        except Exception as ex:
            self.logger.error(ex)
        else:
            send_request=[]
            for data in data_list:
                if data.has_key("Count"):
                    continue

                model = {"court_name": data[u"法院名称"],
                        "case_number": data[u"案号"],
                        "jugement_program": data[u"审判程序"],
                        "case_name": data[u"案件名称"],
                        "jugement_date": data[u"裁判日期"],
                        "case_type": data[u"案件类型"]}

                send_request.append(scrapy.Request(url="http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID={0}".format(data[u"文书ID"]),
                                    meta={"model":model},
                                    callback=self.parse_detail,
                                    errback=self.handle_error))
            return send_request
        pass

    def parse_detail(self,response):
        if response.status == 302:
            self.logger.info("retry redirect url:" + response.url)
            response.request.headers["Referer"] = "http://wenshu.court.gov.cn"
            response.request.dont_filter = True
            return response.request

        model=response.meta["model"]
        model["content"]=response.text
        model["url"]=response.url
        model["createtime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return model

    def handle_error(self, result, *args, **kw):
        self.logger.error("error url is :%s" % result.request.url)

    def __get_wenshu_all_type(self):
        """获取文书类型"""
        client = MongoClient(self.settings["MONGO_URI"], replicaSet=self.settings["MONGO_REPLICAT_SET"])
        db = client[self.settings["MONGO_DATABASE"]]
        db.authenticate(self.settings["MONGO_USERNAME"], self.settings["MONGO_PASSWORD"])
        data = db["menu_base"].find_one()
        if data is None:
            return []

        client.close()
        return data["wenshu_type_name"]

    def __get_judgement_program(self):
        """获取审判程序"""
        client = MongoClient(self.settings["MONGO_URI"], replicaSet=self.settings["MONGO_REPLICAT_SET"])
        db = client[self.settings["MONGO_DATABASE"]]
        db.authenticate(self.settings["MONGO_USERNAME"], self.settings["MONGO_PASSWORD"])
        data = db["menu_base"].find_one()
        if data is None:
            return []

        client.close()
        return data["judgement_program"]

    def __get_judgement_years(self):
        """获取裁判年份"""
        client = MongoClient(self.settings["MONGO_URI"], replicaSet=self.settings["MONGO_REPLICAT_SET"])
        db = client[self.settings["MONGO_DATABASE"]]
        db.authenticate(self.settings["MONGO_USERNAME"], self.settings["MONGO_PASSWORD"])
        data = db["menu_base"].find_one()
        if data is None:
            return []
        client.close()
        return data["judgement_years"]

    def __get_court_area(self):
        """获取法院地域,获取所有没有子菜单的法院"""
        client = MongoClient(self.settings["MONGO_URI"], replicaSet=self.settings["MONGO_REPLICAT_SET"])
        db = client[self.settings["MONGO_DATABASE"]]
        db.authenticate(self.settings["MONGO_USERNAME"], self.settings["MONGO_PASSWORD"])
        data = db["menu_court_area"].find()
        result=[]
        for court_area in data:
            child_count=db["menu_court_area"].find({u"parent":str(court_area["id"])}).count()
            if child_count<=0:
                result.append(court_area)
        client.close()
        return result

    def __get_case_summary(self):
        """获取案由,获取所有没有子菜单的案由"""
        client = MongoClient(self.settings["MONGO_URI"], replicaSet=self.settings["MONGO_REPLICAT_SET"])
        db = client[self.settings["MONGO_DATABASE"]]
        db.authenticate(self.settings["MONGO_USERNAME"], self.settings["MONGO_PASSWORD"])
        data = db["menu_case_summary"].find()
        result=[]
        for case_summary in data:
            child_count=db["menu_case_summary"].find({u"parent":case_summary["id"]}).count()
            if child_count<=0:
                result.append(case_summary)
        client.close()
        return result