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
#江西律师抓取
class JiangXiLawyerSpider(scrapy.Spider):
    name = "jiangxi_law_spider"
    start_urls = ["http://lawnew.jxsf.gov.cn/views/lawyerInfo/findLawyer.jsp"]
    areaData = AreaData()
    userInfoInfoData= UserInfoInfoData()
    pagesize=20
    provincode='38'
    baseurl = "http://lawnew.jxsf.gov.cn/flfw-jx/portEmpLs/queryLSList?{0}"
    def parse(self, response):
        province_city_dic=[]
        province_city_dic.append({'citycode':'3601','cityname':u'南昌市'})
        province_city_dic.append({'citycode': '3602', 'cityname': u'景德镇市'})
        province_city_dic.append({'citycode': '3603', 'cityname': u'萍乡市'})
        province_city_dic.append({'citycode': '3604', 'cityname': u'九江市'})
        province_city_dic.append({'citycode': '3605', 'cityname': u'新余市'})
        province_city_dic.append({'citycode': '3606', 'cityname': u'鹰潭市'})
        province_city_dic.append({'citycode': '3607', 'cityname': u'赣州市'})
        province_city_dic.append({'citycode': '3608', 'cityname': u'吉安市'})
        province_city_dic.append({'citycode': '3609', 'cityname': u'宜春市'})
        province_city_dic.append({'citycode': '3610', 'cityname': u'抚州市'})
        province_city_dic.append({'citycode': '3611', 'cityname': u'上饶市'})
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
        pagecount = int(data['content']['pages'])
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
        data = json.loads(response.body_as_unicode())['content']['list']
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
            item['LawOrg'] = None if data.has_key('swsmc') == False else data['swsmc']
            item['UIEmail'] = None if data.has_key('dzyx') == False else data['dzyx']
            item["UISignature"] = None if data.has_key('grjj') == False else data['grjj']
            item["Address"] = None if data.has_key('deptAdress') == False else data['deptAdress'].replace("\r",'').replace("\n",'').replace(' ','')
            item['UISex'] = None if data.has_key('xb') == False else (0 if data['xb']==u'男' else 1)
            item["CityCode"] = ''.join(self.areaData.find_area_by_name_return_code((cityname)))
            fiil_str = None if data.has_key('ywzcmc') == False else data['ywzcmc']
            if fiil_str != None:
                item['fiil_str'] = field_info_dic.find_field_by_name(fiil_str.split(u","))
            # 头像路径
            dirname = "jiangxi"
            item["UIPic"] = ''.join(
                http_util.downloadImage(['http://lawnew.jxsf.gov.cn/flfw-jx/views/picture/'+data['lszp']], '/AppFile/' + dirname + "/" + item["UIID"] + '/head'))
            return item



    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)