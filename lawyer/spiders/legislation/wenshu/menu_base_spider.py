#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import scrapy

class MenuBaseSpider(scrapy.spiders.Spider):
    name = "menu_base"
    start_urls = [
        "http://wenshu.court.gov.cn/list/list/?sorttype=1"
    ]
    handle_httpstatus_list = [302]

    def parse(self, response):
        if response.status == 302:
            self.logger.info(u"retry url:"+response.url)
            return response.request

        return scrapy.FormRequest(url="http://wenshu.court.gov.cn/List/TreeContent?",
                                  method="POST",
                                  headers={"X-Requested-With":"XMLHttpRequest"},
                                  formdata={"Param":""},
                                  callback=self.parse_menu,
                                  errback=self.handle_error)
        pass

    def parse_menu(self,response):
        menu_list=json.loads(response.text.strip('"').replace("\\",""))
        wenshu_type_name=[]
        judgement_program =[]
        judgement_years=[]
        court_area=[]
        court_layout = []
        one_level_case=[]
        for menu in menu_list:
            child_list=menu["Child"]
            if menu["Key"] ==u"文书类型":
               for child in child_list:
                   name = child["Key"]
                   wenshu_type_name.append({"name":name,"value":child["Value"]})

            if menu["Key"] ==u"审判程序":
               for child in child_list:
                   name = child["Key"]
                   judgement_program.append({"name":name,"value":child["Value"]})

            if menu["Key"] ==u"裁判年份":
               for child in child_list:
                   name = child["Key"]
                   judgement_years.append({"name":name,"value":child["Value"]})
            if menu["Key"] == u"法院地域":
                for child in child_list:
                    if child["Value"] != u"此节点加载中...":
                        court_area.append({"name": child["Key"], "parent": child["parent"], "id": child["id"],
                                           "value": child["Value"]})


            if menu["Key"] ==u"法院层级":
               for child in child_list:
                   name = child["Key"]
                   court_layout.append(name)

            if menu["Key"] == u"一级案由":
                for child in child_list:
                    if child["Value"] != u"此节点加载中...":
                        one_level_case.append({"name":child["Key"],"parent":child["parent"],"id":child["id"],"value":child["Value"]})

        return {"wenshu_type_name":wenshu_type_name,
                "judgement_program":judgement_program,
                "judgement_years":judgement_years,
                "court_area":court_area,
                "court_layout":court_layout,
                "one_level_case":one_level_case}

    def handle_error(self, result, *args, **kw):
        self.logger.error("error url is :%s" % result.request.url)