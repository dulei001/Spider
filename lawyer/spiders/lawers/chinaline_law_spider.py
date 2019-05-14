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
#法律在线律师抓取
class ChinaLineLawyerSpider(scrapy.Spider):
    name = "chinaline_law_spider"
    start_urls = ["http://www.fl900.com"]
    areaData = AreaData()
    userInfoInfoData= UserInfoInfoData()
    baseurl = "http://www.fl900.com/lawyer/0-0-{0}.html"
    def parse(self, response):
        for p in range(1,1551):
            yield scrapy.FormRequest(url=self.baseurl.format(str(p)),
                                     method="GET",
                                     dont_filter=True,
                                     callback=self.parseList,
                                     errback=self.handle_error,
                                     )



    def parseList(self,response):
        for i in response.css(".lawyerlist li a:nth-child(1)"):
            detail_url='http://www.fl900.com'+i.xpath("@href").extract_first()
            uname=i.xpath("img/@alt").extract_first()
            yield scrapy.FormRequest(url=detail_url,
                                     method="GET",
                                     dont_filter=True,
                                     callback=self.parse_detail,
                                     errback=self.handle_error,
                                     meta={'uname':uname}
                                     )

    #详情页面
    def parse_detail(self, response):
        item = {}
        #  #[UIID],[UIPhone] ,[UIName] ,[UIEmail] ,[UIPic],[UILawNumber],[LawOrg],[ProvinceCode],[CityCode],[Address],[UISignature]
        item["UIID"] = str(uuid.uuid1()).replace('-', '')
        uiphone =''.join(response.xpath('/html/body/div[3]/div[2]/div[2]/li[3]/text()').extract()).replace(u'手机：','').replace(u"\xa0",'')
        match_count = len(re.findall(r'[1][3,4,5,6,7,8][0-9]{9}', uiphone))
        item['UILawNumber'] = ''.join(response.xpath('/html/body/div[3]/div[2]/div[1]/ul[1]/li[2]/p[2]/label[1]/text()').extract()).replace(u'执业证号：','').replace(u"\xa0",'')
        if item["UILawNumber"] != None and len(item["UILawNumber"]) == 17 and self.userInfoInfoData.find_lawyer_by_lawlumber((item["UILawNumber"],)) == None :
            item["UIPhone"] = None if match_count == 0 else uiphone
            item['UIName'] = response.meta['uname']
            item['LawOrg'] =''.join(response.xpath('/html/body/div[3]/div[2]/div[1]/ul[1]/li[2]/p[2]/label[2]/text()').extract()).replace(u'执业机构：','').replace(u"\xa0",'')
            item['UIEmail'] = ''.join(response.xpath('/html/body/div[3]/table/tbody/tr[6]/td[4]/text()').extract()).replace('\t','').replace('\n','')
            item["UISignature"]=''.join(response.xpath('/html/body/div[3]/div[2]/div[1]/ul[1]/li[2]/p[1]/text()').extract()).replace(u"\xa0",'')
            item["Address"] = ''.join(response.xpath('/html/body/div[3]/div[2]/div[1]/ul[1]/li[2]/p[2]/label[3]/text()').extract()).replace(u'联系地址：','').replace(u"\xa0",'')
            pro_city_str= ''.join(response.xpath('/html/body/div[3]/div[2]/div[2]/li[1]/text()').extract()).replace(u'地区：','').split(' ')
            item["ProvinceCode"] = ''.join(self.areaData.find_area_by_name_return_code((pro_city_str[0])))
            item["CityCode"] = ''.join(self.areaData.find_area_by_name_return_code((pro_city_str[1])))
            # 头像路径
            dirname='fl900'
            item["UIPic"] = '/APPFile/head.jpg'
            fiil_str=response.css('.goodat span::text').extract()
            if fiil_str != None:
                item['fiil_str'] = field_info_dic.find_field_by_name(fiil_str)
            item['url'] = response.url
            return item



    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)