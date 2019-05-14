#!/usr/bin/python
#-*- coding: utf-8 -*-
import json
import uuid

import re
import scrapy
import time

from dal.service.AreaData import AreaData
from dal.service.UserInfoInfoData import UserInfoInfoData
from lawyer import http_util
from   lawyer.spiders.lawers.field_info_dic import field_info_dic
#河北律师抓取
class HeBeiLawyerSpider(scrapy.Spider):
    name = "hebei_law_spider"
    start_urls = ["http://he.12348.gov.cn/skywcm/webpage/search/index.jsp"]
    areaData = AreaData()
    userInfoInfoData= UserInfoInfoData()
    pagesize=20
    provincode='13'
    baseurl = "http://he.12348.gov.cn/skywcm/webpage/search/search_do.jsp"
    def parse(self, response):
        isflag=0
        for item in  response.xpath("//dl[@class='searchTab1']/dd"):
            if isflag<3:
                isflag=isflag+1
                continue
            citycode =item.xpath('@data').extract_first().replace(u"{districtcode:'","").replace(u"'}",'')
            cityname = item.xpath('a/text()').extract_first()
            yield scrapy.FormRequest(url=self.baseurl,
                                     method="POST",
                                     headers={'X-Requested-With': 'XMLHttpRequest'},
                                     dont_filter=True,
                                     callback=self.parseAjaxPageList,
                                     errback=self.handle_error,
                                     meta={'areacode':citycode,'cityname':cityname},
                                     formdata={ "pageNum":'1','pageSize':str(self.pagesize),'districtcode':citycode,'type':'2','businessType':'1','pkid':'0','t':str(int(time.time()))}
                                     )

    def parseAjaxPageList(self,response):
        data = json.loads(response.body_as_unicode())
        pagecount = int(data['pageCount'])
        for page  in range(1,pagecount):
            yield scrapy.FormRequest(url=self.baseurl,
                                     method="POST",
                                     headers={'X-Requested-With': 'XMLHttpRequest'},
                                     dont_filter=True,
                                     callback=self.parseAjaxList,
                                     errback=self.handle_error,
                                     meta={ 'cityname': response.meta["cityname"]},
                                     formdata={"pageNum": str(page), 'pageSize':str(self.pagesize), 'districtcode': response.meta['areacode'],'type':'2','businessType':'1','pkid':'0','t':str(int(time.time()))})



    def parseAjaxList(self,response):
        data = json.loads(response.body_as_unicode())
        for item in data['datas']:
             item['cityname']=response.meta['cityname']
             yield  self.parse_detail(item)


    #详情页面
    def parse_detail(self, data):
        item = {}
        #  #[UIID],[UIPhone] ,[UIName] ,[UIEmail] ,[UIPic],[UILawNumber],[LawOrg],[ProvinceCode],[CityCode],[Address],[UISignature]
        item["UIID"] = str(uuid.uuid1()).replace('-', '')
        uiphone =''  if data.has_key('cell_phone')==False else data['cell_phone']
        match_count = len(re.findall(r'[1][3,4,5,6,7,8][0-9]{9}', uiphone))
        item['UILawNumber'] = None  if data.has_key('accountcode')==False else data['accountcode']
        if item["UILawNumber"] != None and len(item["UILawNumber"]) == 17 and self.userInfoInfoData.find_lawyer_by_lawlumber((item["UILawNumber"],)) == None :
            item["UIPhone"] = None if match_count == 0 else uiphone
            item['UIName'] = data['user_name']
            item["ProvinceCode"] = self.provincode
            item['LawOrg'] =  None  if data.has_key('accountorg')==False else data['accountorg']
            item['UIEmail'] =None if data.has_key('email')==False else data['email']
            item["UISignature"]=None
            item["Address"] =  None  if data.has_key('address')==False else data['address']
            item['UISex']=0 if  data['sex']==1 else 1
            item["CityCode"] = ''.join(self.areaData.find_area_by_name_return_code((data['cityname'])))
            # 头像路径
            dirname="shandong"
            item["UIPic"] = ''.join(http_util.downloadImage([data['picImg']], '/AppFile/'+ dirname+"/"+ item["UIID"] + '/head'))
            return item



    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)