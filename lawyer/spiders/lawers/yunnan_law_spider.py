#!/usr/bin/python
#-*- coding: utf-8 -*-
import json
import uuid

import re
import scrapy

from dal.service.AreaData import AreaData
from dal.service.UserInfoInfoData import UserInfoInfoData
from lawyer import http_util
from   lawyer.spiders.lawers.field_info_dic import field_info_dic
#云南律师抓取
class YunNanLawyerSpider(scrapy.Spider):
    name = "yunnan_law_spider"
    start_urls = ["http://12348.yn.gov.cn/lsfw/index"]
    areaData = AreaData()
    userInfoInfoData= UserInfoInfoData()
    pagesize=20
    provincode='53'
    baseurl = "http://12348.yn.gov.cn/lsfw/queryLs"
    def parse(self, response):
        for item in  response.css("#szds span::text").extract():
            yield scrapy.FormRequest(url=self.baseurl,
                                     method="POST",
                                     headers={'X-Requested-With': 'XMLHttpRequest','Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
                                     dont_filter=True,
                                     callback=self.parseAjaxPageList,
                                     errback=self.handle_error,
                                     meta={'cityname':item},
                                     formdata={ "page":'1','CFwdq':[]}
                                     )


    def parseAjaxPageList(self,response):
        data = json.loads(response.body_as_unicode())
        pagecount = int(data['data']['data']['totalPage'])
        for page  in range(1,pagecount):
            yield scrapy.FormRequest(url=self.baseurl,
                                     method="POST",
                                     headers={'X-Requested-With': 'XMLHttpRequest'},
                                     dont_filter=True,
                                     callback=self.parseAjaxList,
                                     errback=self.handle_error,
                                     meta={'cityname': response.meta['cityname']},
                                     formdata={"page": str(page), 'CFwdq': []})




    def parseAjaxList(self,response):
        print json.loads(response.body_as_unicode())
        data = json.loads(response.body_as_unicode())['data']['data']
        for item in data['results']:
            yield self.parse_detail(item,response.meta['cityname'])


     # 详情页面
    def parse_detail(self, data,cityname):
            item = {}
            #  #[UIID],[UIPhone] ,[UIName] ,[UIEmail] ,[UIPic],[UILawNumber],[LawOrg],[ProvinceCode],[CityCode],[Address],[UISignature]
            item["UIID"] = str(uuid.uuid1()).replace('-', '')
            uiphone = '' if data.has_key('cSjhm') == False else data['cSjhm']
            match_count = len(re.findall(r'[1][3,4,5,6,7,8][0-9]{9}', uiphone))
            item['UILawNumber'] = None if data.has_key('cZyzh') == False else data['cZyzh']
            if item["UILawNumber"] != None and len(item["UILawNumber"]) == 17 and self.userInfoInfoData.find_lawyer_by_lawlumber((item["UILawNumber"],)) == None:
                item["UIPhone"] = None if match_count == 0 else uiphone
                item['UIName'] = data['cXm']
                item["ProvinceCode"] = self.provincode
                item['LawOrg'] = None if data.has_key('tJg') == False else data['tJg']['cMc']
                item['UIEmail'] = None if data.has_key('cDzyx') == False else data['cDzyx']
                item["UISignature"] = None
                item["Address"] = None if data.has_key('cXxdz') == False else data['cXxdz']
                item['UISex'] = None if data.has_key('cXb') == False else int(data['cXb'])
                item["CityCode"] = ''.join(self.areaData.find_area_by_name_return_code((cityname)))
                fiil_str=None if data.has_key('cScajMc') == False else data['cScajMc']
                if fiil_str!=None:
                    item['fiil_str'] = field_info_dic.find_field_by_name(fiil_str.split(u";"))
                # 头像路径
                dirname = "yunnan"
                item["UIPic"] = ''.join(http_util.downloadImage([data['cTx']], '/AppFile/' + dirname + "/" + item["UIID"] + '/head'))
                return item


    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)