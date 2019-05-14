#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import math
import os
import re
import traceback
from datetime import datetime
from urllib import quote
import requests
import scrapy
import sys
from pymongo import MongoClient
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy_redis.spiders import RedisSpider
from scrapy_redis.utils import bytes_to_str
from twisted.internet.error import DNSLookupError, TimeoutError, TCPTimedOutError
from devops import scrapyd_cencel
from devops import scrapyd_deploy
from devops import scrapyd_scheduling


class WenshuLawyerFirmSpider(RedisSpider):
    redis_key="wenshu_lawyer_firm:start_urls"
    name = "wenshu_lawyer_firm_spider"
    handle_httpstatus_list = [302]

    def make_request_from_data(self, data):
        try:
            param = json.loads(bytes_to_str(data, self.redis_encoding))
            lawyer_Id=param["lawyer_Id"]
            lawyer = param["lawyer"]
            firm = param["firm"]
            url = self.__build_url(lawyer, firm)
        except Exception as ex:
            self.logger.error(ex)
            self.logger.error(traceback.format_exc())
        else:
            return scrapy.Request(url=url,
                                  dont_filter=True,
                                  method="GET",
                                  headers={"Referer": "http://wenshu.court.gov.cn"},
                                  callback=self.parse,
                                  meta={"lawyer": lawyer, "firm": firm,"lawyer_Id":lawyer_Id},
                                  errback=self.handle_error)

    def __build_url(self, lawyer, firm):
       lawyer=lawyer.encode("utf8")
       firm = firm.encode("utf8")
       return u"http://wenshu.court.gov.cn/list/list/?sorttype=1&conditions=searchWord+" + quote(lawyer) + u"+LAWYER++" + quote("律师") + ":" + quote(lawyer)+u"&conditions=searchWord+" + quote(firm) + u"+LS++" + quote("律所") + ":" + quote(firm)


    def parse(self,response):
        if response.status == 302:
            self.logger.info("app retry redirect url:" + response.url)
            response.request.headers["Referer"] = "http://wenshu.court.gov.cn"
            response.request.dont_filter = True
            return response.request

        lawyer=response.meta["lawyer"]
        firm = response.meta["firm"]
        lawyer_Id = response.meta["lawyer_Id"]
        self.request = scrapy.FormRequest(url="http://wenshu.court.gov.cn/List/ListContent",
                                          method="POST",
                                          dont_filter=True,
                                          meta={"lawyer":lawyer,"firm":firm,"lawyer_Id":lawyer_Id},
                                          headers={"X-Requested-With": "XMLHttpRequest"},
                                          formdata={"Param": self.__build_param(lawyer, firm),
                                                    "Index": str(1),
                                                    "Page": "20",
                                                    "Order": u"法院层级",
                                                    "Direction": "asc"},
                                          callback=self.parse_page_count,
                                          errback=self.handle_error)
        return self.request

    def parse_page_count(self, response):
        print "start page count"
        if response.status == 302:
            self.logger.info("retry redirect url:" + response.url)
            response.request.headers["Referer"] = "http://wenshu.court.gov.cn"
            response.request.dont_filter = True

        lawyer = response.meta["lawyer"]
        firm = response.meta["firm"]
        lawyer_Id = response.meta["lawyer_Id"]

        next_requests = []
        try:
            data_list= json.loads(response.text.replace("\\", "").strip('"'))
        except Exception as ex:
            self.logger.error(self.__format_exception_message(response))
        else:
            page_count= self.__find_document_page_count(data_list)

            for index in range(1, int(page_count)+1):
                 next_requests.append(scrapy.FormRequest(url="http://wenshu.court.gov.cn/List/ListContent",
                                                                                method="POST",
                                                                                dont_filter=True,
                                                                                meta={"lawyer":lawyer,"firm":firm,"lawyer_Id":lawyer_Id},
                                                                                headers={"X-Requested-With": "XMLHttpRequest"},
                                                                                formdata={"Param": self.__build_param(lawyer,firm),
                                                                                          "Index": str(index),
                                                                                          "Page": "20",
                                                                                          "Order": u"法院层级",
                                                                                          "Direction": "asc"},
                                                                                callback=self.parse_page_list,
                                                                                errback=self.handle_error))
            return next_requests

    def __find_document_page_count(self, data_list):
        for data in data_list:
            if data.has_key("Count"):
                page_count = int(data["Count"])
                if (page_count > 20):
                    return math.ceil(page_count / 20.0)
                else:
                    return 1

    def parse_page_list(self, response):
        print "start page list"

        """解析列表页"""
        if response.status == 302:
            self.logger.info("retry redirect url:" + response.url)
            response.request.headers["Referer"] = "http://wenshu.court.gov.cn"
            response.request.dont_filter = True
            return response.request

        lawyer = response.meta["lawyer"]
        firm = response.meta["firm"]
        lawyer_Id = response.meta["lawyer_Id"]
        next_request = []
        try:
            data_list = json.loads(response.text.replace("\\", "").strip('"'))
        except Exception as ex:
            error_message = self.__format_exception_message(response)
            self.logger.error(ex)
            self.logger.error(error_message)
        else:
            for data in data_list:
                if data.has_key("Count"):
                    continue

                if (self.__existed_doc(data[u"文书ID"],lawyer,firm)):
                    self.logger.log(u"重复的文书ID ："+data[u"文书ID"])
                    continue

                model = {
                    "doc_id": data[u"文书ID"],
                    "title": data[u"案件名称"],
                    "case_number": data[u"案号"],
                    "case_type_number": data[u"案件类型"],
                    "lawyer":lawyer,
                    "firm":firm,
                    "lawyer_Id":lawyer_Id
                }
                model["createtime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                model["collection"] = "lawyer_firm_document"
                model["source"] = u"中国裁判文书网"
                model["status"]=0
                model["url"] = "http://wenshu.court.gov.cn/content/content?DocID={0}".format(model["doc_id"])

                next_request.append(scrapy.Request(url= "http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID={0}".format(model["doc_id"]),
                                           meta={"model": model},
                                           dont_filter=True,
                                           callback=self.parse_content,
                                           errback=self.handle_error))
        return next_request

    def parse_content(self, response):
        print "start content"
        if response.status == 302:
            self.logger.info("retry redirect url:" + response.url)
            response.request.headers["Referer"] = "http://wenshu.court.gov.cn"
            response.request.dont_filter = True
            return response.request

        try:
            model = response.meta["model"]
            model["publish_date"] = "".join(re.findall(r'\\"PubDate\\":\\"(.+)\\",', response.text))
            model["content"] = "".join(re.findall(r'\\"Html\\":\\"(.+?)\\"}', response.text))
        except Exception as ex:
            self.logger.error(ex)
            self.logger.error(u"解析内容出错 document url: {0}".format(model["url"]))
            return model
        else:
            return scrapy.FormRequest(url="http://wenshu.court.gov.cn/Content/GetSummary",
                                      method="POST",
                                      dont_filter=True,
                                      meta={"model": model},
                                      headers={"X-Requested-With": "XMLHttpRequest"},
                                      formdata={"docId": model["doc_id"]},
                                      callback=self.parse_summary,
                                      errback=self.handle_error)

    def parse_summary(self, response):
        print "start summary"

        model = response.meta["model"]
        object_string = response.text.replace("\u0027", '"').replace("\\", "").strip('"')
        try:
            result = self.__convert_javascript_object_string__to_json(object_string)
        except Exception as ex:
            self.logger.error(ex)
            self.logger.error(u"解析summary出错 document url: {0}".format(model["url"]))
            return model

        data = result['data']
        if (result["code"] != 1):
            return model

        for relateInfo in data["RelateInfo"]:
            if relateInfo["name"] == u"审理法院":
                model["court_name"] = relateInfo["value"]
            if relateInfo["name"] == u"案件类型":
                model["case_type"] = relateInfo["value"]
            if relateInfo["name"] == u"案由":
                model["case_brief"] = relateInfo["value"]
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

    def __existed_doc(self, doc_id,lawyer,firm):
        spider_env = os.getenv("SPIDER_ENV", "dev")
        if spider_env != "product":
            return False

        client = MongoClient(self.settings["MONGO_URI"], replicaSet=self.settings["MONGO_REPLICAT_SET"])
        db = client[self.settings["MONGO_DATABASE"]]
        db.authenticate(self.settings["MONGO_USERNAME"], self.settings["MONGO_PASSWORD"])
        result = db["lawyer_firm_document"].count({"doc_id": doc_id,"lawyer":lawyer,"firm":firm,"status":0})
        return result > 0

    def __convert_javascript_object_string__to_json(self, object_string):
        "将javascript 对象的string表示形式转换成json对象"
        response = requests.post(self.settings["CONVERT_JOSN_URL"], {"object_string": object_string})
        return response.json()

    def __build_param(self, lawyer, firm):
        param = []
        if lawyer is not None:
            param.append(u"律师:" + lawyer)
        if firm is not None:
            param.append(u"律所:" + firm)

        return ",".join(param)

    def __format_exception_message(self, response):
        error_message_list = []
        error_message_list.append(u"堆栈信息:" + traceback.format_exc())
        error_message_list.append(u"response结果:" + response.text)
        error_message_list.append(u"request参数:" + response.request.formdata)
        return u"\r".join(error_message_list)

    def handle_error(self, failure):
        self.logger.error(repr(failure))
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)
        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)
        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)





if __name__ == "__main__":
    # for index in range(8):
    #     # 部署整个工程
    #     scrapyd_deploy.deploy()
    #     # 运行spider
    #     print scrapyd_scheduling.schedule(project="lawyer", spider=WenshuLawyerFirmSpider.name)
    # 取消运行spder 执行三次
          print scrapyd_cencel.cancel(project="lawyer",job="c9b1e7103aaa11e786230242c0a80003")

