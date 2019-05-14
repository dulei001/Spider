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
#宁夏律师抓取
class NingXiaLawyerSpider(scrapy.Spider):
    name = "ningxia_law_spider"
    start_urls = ["http://nx.12348.gov.cn/flfw-xt/views/new_front/ls/lsfw.jsp"]
    areaData = AreaData()
    userInfoInfoData= UserInfoInfoData()
    pagesize=20
    provincode='64'
    baseurl = "http://nx.12348.gov.cn/flfw-xt/portEmpLs/queryLsInfoByCity?{0}"
    def parse(self, response):
        province_city_dic=[]
        province_city_dic.append({'citycode':'6401','cityname':u'银川市'})
        province_city_dic.append({'citycode': '6402', 'cityname': u'石嘴山市'})
        province_city_dic.append({'citycode': '6403', 'cityname': u'吴忠市'})
        province_city_dic.append({'citycode': '6404', 'cityname': u'固原市'})
        province_city_dic.append({'citycode': '6405', 'cityname': u'中卫市'})
        for item in  province_city_dic:
            news_url=self.baseurl.format("pageSize="+str(self.pagesize)+"&pageNum=1&city="+item['citycode']+"&selInfo=&ywzc=&_="+str(int(time.time())))
            yield scrapy.Request(url=news_url,
                                     method="GET",
                                     dont_filter=True,
                                     callback=self.parseAjaxPageList,
                                     errback=self.handle_error,
                                     meta={'cityname':item['cityname']},
                                     )

    def parseAjaxPageList(self,response):
        data = json.loads(response.body_as_unicode())
        pagecount = (int(data['total'])-1)/(self.pagesize+1)
        for page  in range(1,pagecount):
            page_url = re.sub('&pageNum=\d+', '&pageNum='+str(page), response.url)
            detail_url = re.sub('&_=.*', '&_=' + str(int(time.time())), page_url)
            yield scrapy.Request(url=detail_url,
                                     method="GET",
                                     dont_filter=True,
                                     callback=self.parseAjaxList,
                                     errback=self.handle_error,
                                     meta={'cityname': response.meta['cityname']},)

    def parseAjaxList(self, response):
        data = json.loads(response.body_as_unicode())['content']
        for item in data:
            yield self.parse_detail(item, response.meta['cityname'])
            # 详情页面

    def parse_detail(self, data, cityname):
        item = {}
        #  #[UIID],[UIPhone] ,[UIName] ,[UIEmail] ,[UIPic],[UILawNumber],[LawOrg],[ProvinceCode],[CityCode],[Address],[UISignature]
        item["UIID"] = str(uuid.uuid1()).replace('-', '')
        uiphone = '' if data.has_key('sjhm') == False else data['sjhm']
        match_count = len(re.findall(r'[1][3,4,5,6,7,8][0-9]{9}', uiphone))
        item['UILawNumber'] = None if data.has_key('zyzh') == False else data['zyzh']
        if item["UILawNumber"] != None and len(
                item["UILawNumber"]) == 17 and self.userInfoInfoData.find_lawyer_by_lawlumber(
                (item["UILawNumber"],)) == None:
            item["UIPhone"] = None if match_count == 0 else uiphone
            item['UIName'] = data['lsxm']
            item["ProvinceCode"] = self.provincode
            item['LawOrg'] = None if data.has_key('deptName') == False else data['deptName']
            item['UIEmail'] = None if data.has_key('dzyx') == False else data['dzyx']
            item["UISignature"] = None if data.has_key('grjj') == False else data['grjj']
            item["Address"] = None if data.has_key('lxdz') == False else data['lxdz'].replace("\r",'').replace("\n",'').replace(' ','')
            item['UISex'] = None if data.has_key('xbMc') == False else (0 if data['xbMc']==u'男' else 1)
            item["CityCode"] = ''.join(self.areaData.find_area_by_name_return_code((cityname)))
            fiil_str = None if data.has_key('ywzcmc') == False else data['ywzcmc']
            if fiil_str != None:
                item['fiil_str'] = field_info_dic.find_field_by_name(fiil_str.split(u","))
            # 头像路径
            dirname = "ningxia"
            item["UIPic"] = ''.join(
                http_util.downloadImage(['http://nx.12348.gov.cn/flfw-xt/views/picture/'+data['lszp']], '/AppFile/' + dirname + "/" + item["UIID"] + '/head'))
            return item



    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)