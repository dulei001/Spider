#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from datetime import datetime
import math
import re
import requests
import scrapy
from pymongo import MongoClient

from devops import scrapyd_cencel
from devops import scrapyd_deploy
from devops import scrapyd_scheduling


class WenShu2013To2017Spider(scrapy.spiders.Spider):
    name = "wenshu_2017_jilin_spider"
    start_urls = [
        "http://wenshu.court.gov.cn/list/list/?sorttype=1"
    ]
    handle_httpstatus_list = [302]
    years=["2017"]
    senior_courts=[{"type":u"法院地域", "name": u"吉林省"}]


    def parse(self, response):
        self.logger.info("year:%s" % ",".join(self.years))
        for senior_court in self.senior_courts:
            self.logger.info(u"地域:%s" % senior_court["name"])

        if response.status == 302:
            response.request.headers["Referer"] = "http://wenshu.court.gov.cn"
            response.request.dont_filter = True
            self.logger.info("retry redirect url:" + response.url)
            return response.request

        next_requests=[]
        for year in self.years:
            next_requests.append(scrapy.FormRequest(url="http://wenshu.court.gov.cn/List/TreeContent",
                                      method="POST",
                                      dont_filter=True,
                                      meta={"year":year},
                                      headers={"X-Requested-With": "XMLHttpRequest"},
                                      formdata={"Param": self.__build_param(year=year)},
                                      callback=self.parse_keywords_menu,
                                      errback=self.handle_error))
        return next_requests

    def parse_keywords_menu(self,response):
        """"获取年份对应的关键词"""

        if response.status == 302:
            response.request.headers["Referer"] = "http://wenshu.court.gov.cn"
            response.request.dont_filter = True
            self.logger.info("retry redirect url:" + response.url)
            return response.request

        year = response.meta["year"]
        next_requests = []
        menu_list = json.loads(response.text.strip('"').replace("\\", ""))
        keywords=self.__parse_keyword_from_json(menu_list)
        for keyword in keywords:
            for senior_court in self.senior_courts:
                next_requests.append(scrapy.FormRequest(url="http://wenshu.court.gov.cn/List/CourtTreeContent",
                                                        method="POST",
                                                        dont_filter=True,
                                                        meta={"year": year, "keyword": keyword,
                                                              "senior_court": senior_court},
                                                        headers={"X-Requested-With": "XMLHttpRequest"},
                                                        formdata={"Param": self.__build_param(year, keyword, senior_court),"parval": senior_court["name"]},
                                                        callback=self.parse_medium_court_area,
                                                        errback=self.handle_error))

        return next_requests

    def __parse_keyword_from_json(self, menu_list):
        keywords=[]
        for menu in menu_list:
            child_list = menu["Child"]
            if menu["Key"] != u"关键词":
                continue
            for child in child_list:
                name = child["Key"]
                keywords.append(name)
        return keywords

    def parse_medium_court_area(self, response):
        """解析中级法院"""

        if response.status == 302:
            self.logger.info(u"retry url:" + response.url)
            return response.request

        try:
           menus = json.loads(response.text.replace("\\", "").strip('"'))
        except Exception as ex:
           menus=[]

        year = response.meta["year"]
        keyword = response.meta["keyword"]
        senior_court=response.meta["senior_court"]
        medium_courts = self.__parse_court_menu_from_json(menus, u"中级法院")
        if len(medium_courts)==0:
            medium_courts.append(senior_court)

        next_requests = []
        for medium_court in medium_courts:
            next_requests.append(scrapy.FormRequest(url="http://wenshu.court.gov.cn/List/CourtTreeContent",
                                                    method="POST",
                                                    dont_filter=True,
                                                    meta={"year": year, "keyword": keyword,"senior_court":senior_court,"medium_court":medium_court},
                                                    headers={"X-Requested-With": "XMLHttpRequest"},
                                                    formdata={"Param": self.__build_param(year=year, keyword=keyword, court=medium_court),
                                                              "parval": medium_court["name"]},
                                                    callback=self.parse_basis_court_area,
                                                    errback=self.handle_error))
        return next_requests

    def parse_basis_court_area(self, response):
        """解析基层法院"""
        if response.status == 302:
            self.logger.info(u"retry url:" + response.url)
            return response.request

        try:
            menus = json.loads(response.text.replace("\\", "").strip('"'))
        except Exception as ex:
            menus=[]
        year=response.meta["year"]
        keyword=response.meta["keyword"]
        senior_court = response.meta["senior_court"]
        medium_court = response.meta["medium_court"]
        next_requests=[]
        basis_courts = self.__parse_court_menu_from_json(menus, u"基层法院")
        if len(basis_courts)==0:
            basis_courts.append(response.meta["medium_court"])

        for basis_court in basis_courts:
            next_requests.append(scrapy.FormRequest(url="http://wenshu.court.gov.cn/List/ListContent",
                                                    method="POST",
                                                    dont_filter=True,
                                                    meta={"year":year, "keyword":keyword,"senior_court": senior_court, "medium_court": medium_court,"basis_court":basis_court},
                                                    headers={"X-Requested-With": "XMLHttpRequest"},
                                                    formdata={"Param": self.__build_param(year=year, keyword=keyword,court=basis_court),
                                                              "Index": str(1),
                                                              "Page": "20",
                                                              "Order": u"法院层级",
                                                              "Direction": "asc"},
                                                    callback=self.parse_page_count,
                                                    errback=self.handle_error))

        return next_requests

    def parse_page_count(self,response):
        """解析数据个数"""
        if response.status == 302:
            self.logger.info("retry redirect url:" + response.url)
            response.request.headers["Referer"] = "http://wenshu.court.gov.cn"
            response.request.dont_filter = True
            return response.request

        next_requests = []
        try:
            data_list = json.loads(response.text.replace("\\", "").strip('"'))
        except Exception as ex:
            self.logger.error(ex)
        else:
            keyword=response.meta["keyword"]
            basis_court = response.meta["basis_court"]
            for data in data_list:
                if data.has_key("Count"):
                    year=response.meta["year"]
                    count=int(data["Count"])
                    if(count>20):
                        page=math.floor(count/20)
                        for index in range(1, int(page)+1):
                            next_requests.append(scrapy.FormRequest(url="http://wenshu.court.gov.cn/List/ListContent",
                                                           method="POST",
                                                           dont_filter=True,
                                                           meta=response.meta,
                                                           headers={"X-Requested-With": "XMLHttpRequest"},
                                                           formdata={"Param": self.__build_param(year=year,keyword=keyword,court=basis_court),
                                                                     "Index": str(index),
                                                                     "Page": "20",
                                                                     "Order": u"法院层级",
                                                                     "Direction": "asc"},
                                                           callback=self.parse_page_list,
                                                           errback=self.handle_error))
                    else:
                        next_requests.append(scrapy.FormRequest(url="http://wenshu.court.gov.cn/List/ListContent",
                                                       method="POST",
                                                       dont_filter=True,
                                                       meta=response.meta,
                                                       headers={"X-Requested-With": "XMLHttpRequest"},
                                                       formdata={"Param": self.__build_param(year=year,keyword=keyword,court=basis_court), "Index": str(1), "Page": "20",
                                                                 "Order": u"法院层级",
                                                                 "Direction": "asc"},
                                                       callback=self.parse_page_list,
                                                       errback=self.handle_error))
                    return next_requests
        return next_requests

    def parse_page_list(self, response):
        """解析列表页"""
        if response.status == 302:
            self.logger.info("retry redirect url:" + response.url)
            response.request.headers["Referer"] = "http://wenshu.court.gov.cn"
            response.request.dont_filter = True
            return response.request
        try:
            data_list = json.loads(response.text.replace("\\", "").strip('"'))
        except Exception as ex:
            self.logger.error(ex)
        else:
            next = []
            for data in data_list:
                if data.has_key("Count"):
                    continue

                if (self.__existed_doc(data[u"文书ID"])):
                    continue

                model = {
                         "doc_id": data[u"文书ID"],
                         "title": data[u"案件名称"],
                         "case_number": data[u"案号"],
                         "case_type_number":data[u"案件类型"],
                         "senior_court":response.meta["senior_court"],
                         "medium_court": response.meta["medium_court"],
                         "basis_court": response.meta["basis_court"],
                         "keyword":response.meta["keyword"],
                         "year": response.meta["year"]
                       }
                model["createtime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                model["collection"] = "caipanwenshu"
                model["source"] = u"中国裁判文书网"
                model["url"] = "http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID={0}".format(model["doc_id"])

                next.append(scrapy.Request(url= model["url"],
                                           meta={"model": model},
                                           dont_filter=True,
                                           callback=self.parse_content,
                                           errback=self.handle_error))
            return next

    def parse_content(self, response):
        if response.status == 302:
            self.logger.info("retry redirect url:" + response.url)
            response.request.headers["Referer"] = "http://wenshu.court.gov.cn"
            response.request.dont_filter = True
            return response.request

        model = response.meta["model"]
        model["publish_date"] = "".join(re.findall(r'\\"PubDate\\":\\"(.+)\\",', response.text))
        model["content"]= "".join(re.findall(r'\\"Html\\":\\"(.+?)\\"}', response.text))

        return scrapy.FormRequest(url="http://wenshu.court.gov.cn/Content/GetSummary",
                                                           method="POST",
                                                           dont_filter=True,
                                                           meta={"model":model},
                                                           headers={"X-Requested-With": "XMLHttpRequest"},
                                                           formdata={"docId":model["doc_id"]},
                                                           callback=self.parse_summary,
                                                           errback=self.handle_error)

    def parse_summary(self,response):
        model= response.meta["model"]
        object_string=response.text.replace("\u0027",'"').replace("\\","").strip('"')
        result=self.__convert_javascript_object_string__to_json(object_string)
        data=result['data']
        if(result["code"]!=1):
            return model

        for relateInfo in data["RelateInfo"]:
            if relateInfo["name"] == u"审理法院":
                model["court_name"]=relateInfo["value"]
            if relateInfo["name"] == u"案件类型":
                model["case_type"]=relateInfo["value"]
            if relateInfo["name"] == u"案由":
                model["court_reason"]=relateInfo["value"]
            if relateInfo["name"] == u"审理程序":
                model["judgement_order"] = relateInfo["value"]
            if relateInfo["name"] == u"裁判日期":
                model["jugement_date"] = relateInfo["value"]
            if relateInfo["name"] == u"当事人":
                model["client"] = relateInfo["value"].split(",")

        # 处理相关法条
        model["legal"] = []
        for legalBase in data["LegalBase"]:
            items = []
            for item in legalBase["Items"]:
                items.append({"name": item[u"法条名称"], "content": item[u"法条内容"]})
            model["legal"].append({"name": legalBase[u"法规名称"], "items": items})

        return model

    def handle_error(self, result, *args, **kw):
       self.logger.error("error url is :%s" % result.request.url)

    def __existed_doc(self, doc_id):
        """获取法院地域,获取所有没有子菜单的法院"""
        client = MongoClient(self.settings["MONGO_URI"], replicaSet=self.settings["MONGO_REPLICAT_SET"])
        db = client[self.settings["MONGO_DATABASE"]]
        db.authenticate(self.settings["MONGO_USERNAME"], self.settings["MONGO_PASSWORD"])
        result = db["caipanwenshu"].count({"doc_id": doc_id})
        return result > 0

    def __convert_javascript_object_string__to_json(self,object_string):
        "将javascript 对象的string表示形式转换成json对象"
        response = requests.post(self.settings["CONVERT_JOSN_URL"], {"object_string": object_string})
        return response.json()

    def __parse_court_menu_from_json(self, menus, type):
        courts=[]
        for menu in menus:
            if menu["Key"] != type:
                continue

            child_list = menu["Child"]
            for child in child_list:
                if child["Value"] == u"此节点加载中..."or int(child["Value"])==0:
                    continue
                courts.append({"name": child["Key"],"parent": child["parent"],"id": child["id"], "value": child["Value"],"type":type})

        return courts

    def __build_param(self,year=None,keyword=None,court=None):
        param = []
        if year is not None:
            param.append(u"裁判年份:" + year)
        if keyword is not None:
            param.append(u"关键词:" + keyword)

        #法院地域
        if court is not None:
            param.append(court["type"] +u":"+ court["name"])
        return ",".join(param)



if __name__ == "__main__":
    # 部署整个工程
    scrapyd_deploy.deploy()
    # 运行spider
    print scrapyd_scheduling.schedule(project="lawyer", spider=WenShu2013To2017Spider.name)
    # 取消运行spder 执行三次
    # print scrapyd_cencel.cancel(project="lawyer",job="0d7cbe5e3e9111e786230242c0a80003")



