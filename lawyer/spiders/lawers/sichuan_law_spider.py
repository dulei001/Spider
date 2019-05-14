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
#四川律师抓取
class SiChuanLawyerSpider(scrapy.Spider):
    name = "sichuan_law_spider"
    start_urls = ["http://fwpt.scsf.gov.cn/lsfw/lsfw.shtml"]
    areaData = AreaData()
    userInfoInfoData= UserInfoInfoData()
    pagesize=20
    provincode='51'
    baseurl = "http://fwpt.scsf.gov.cn/lsfw/lsfwlist.shtml"
    def parse(self, response):
        for item in  response.css(".dropdown a"):
            prostr = ''.join(item.xpath("@onclick").extract())
            citycode =prostr.replace(u"sfjdjg('",'').replace(u"')",'')
            cityname = ''.join(item.xpath("text()").extract())
            yield scrapy.FormRequest(url=self.baseurl,
                                     method="POST",
                                     headers={'X-Requested-With': 'XMLHttpRequest'},
                                     dont_filter=True,
                                     callback=self.parseAjaxPageList,
                                     errback=self.handle_error,
                                     meta={'areacode':citycode,'cityname':cityname},
                                     formdata={ "page":'1','fydm':citycode,'kplb':'2'}
                                     )

    def parseAjaxPageList(self,response):
        pagecount = int(''.join(response.xpath(u'//a[last()]/@onclick').extract()).replace(u'query(','').replace(u')',''))
        for page  in range(1,pagecount):
            yield scrapy.FormRequest(url=self.baseurl,
                                     method="POST",
                                     headers={'X-Requested-With': 'XMLHttpRequest'},
                                     dont_filter=True,
                                     callback=self.parseAjaxList,
                                     errback=self.handle_error,
                                     meta={'areacode': response.meta['areacode'], 'cityname': response.meta['cityname']},
                                     formdata={"page": str(page), 'fydm': response.meta['areacode'], 'kplb': '2'}
                                     )


    def parseAjaxList(self,response):
        for i in response.xpath("//div[@class='synopsis_N fl']/a/@href").extract():
            detail_url='http://fwpt.scsf.gov.cn/'+i
            yield scrapy.Request(url=detail_url,
                                     method="GET",
                                     dont_filter=True,
                                     callback=self.parse_detail,
                                     errback=self.handle_error,
                                     meta={'cityname':response.meta['cityname']},
                                     )

    #详情页面
    def parse_detail(self, response):
        item = {}
        #  #[UIID],[UIPhone] ,[UIName] ,[UIEmail] ,[UIPic],[UILawNumber],[LawOrg],[ProvinceCode],[CityCode],[Address],[UISignature]
        item["UIID"] = str(uuid.uuid1()).replace('-', '')
        uiphone =''.join(response.xpath('/html/body/div[3]/table/tbody/tr[5]/td[4]/text()').extract()).replace('\t','').replace('\n','')
        match_count = len(re.findall(r'[1][3,4,5,6,7,8][0-9]{9}', uiphone))
        item['UILawNumber'] = ''.join(response.css('.font18::text').extract()).replace(u'执业证号 (','').replace(u')','').replace(u"\xa0",'')
        if item["UILawNumber"] != None and len(item["UILawNumber"]) == 17 and self.userInfoInfoData.find_lawyer_by_lawlumber((item["UILawNumber"],)) == None :
            item["UIPhone"] = None if match_count == 0 else uiphone
            item['UIName'] = ''.join(response.css('.font28::text').extract())
            item["ProvinceCode"] = self.provincode
            item['LawOrg'] =''.join(response.css('.lsjjxg3::text').extract()).replace('\t','').replace('\n','')
            item['UIEmail'] = ''.join(response.xpath('/html/body/div[3]/table/tbody/tr[6]/td[4]/text()').extract()).replace('\t','').replace('\n','')
            item["UISignature"]=None
            item["Address"] = None
            item["CityCode"] = ''.join(self.areaData.find_area_by_name_return_code((response.meta['cityname'])))
            # 头像路径
            dirname='sichuan'
            head_url=''.join(response.xpath('/html/body/div[3]/table/tbody/tr[1]/td[1]/img/@src').extract())
            item["UIPic"] = ''.join(http_util.downloadImage(["http://sd.12348.gov.cn/" + head_url], '/AppFile/'+ dirname+"/"+ item["UIID"] + '/head'))
            item['url'] = response.url
            return item



    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)