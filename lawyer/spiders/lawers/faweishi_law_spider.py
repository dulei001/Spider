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
#法卫士律师抓取
class FaWeiShiLawyerSpider(scrapy.Spider):
    name = "faweishi_law_spider"
    start_urls = ["http://m.faweishi.com/lawyer/china/"]
    areaData = AreaData()
    userInfoInfoData= UserInfoInfoData()
    baseurl = "http://m.faweishi.com/ajax.php"
    def parse(self, response):
         for item in response.xpath("//div[@class='fenl'][2]/ul/li/a"):
              yield scrapy.Request(url="http://m.faweishi.com"+item.xpath('@href').extract_first(),
                                       method="GET",
                                       dont_filter=True,
                                       callback=self.parse_province,
                                       errback=self.handle_error,
                                       meta={'province':item.xpath('text()').extract_first(),'start':str(1)}
                                     )


    def parse_province(self,response):
            requests_arr=[]
            where =  response.css('.lawList::attr("w")').extract_first()
            if where != None:
                requests_arr.extend(self.parse_province_list(response))
                start = str(int(response.meta['start'])+1)
                requests_arr.append(scrapy.FormRequest(url=self.baseurl,
                                         method="POST",
                                         headers={'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/x-www-form-urlencoded'},
                                         dont_filter=True,
                                         callback=self.parse_province,
                                         errback=self.handle_error,
                                         formdata={'action':'get_law','start':start,'where': where},
                                         meta={'province': response.meta['province'],'start':start}
                                         ))
                return requests_arr


    def parse_province_list(self,response):
        for item in response.css('.lawList li a::attr(href)').extract():
            yield scrapy.Request(url=item,
                                 method="GET",
                                 dont_filter=True,
                                 callback=self.parse_detail,
                                 errback=self.handle_error,
                                 meta={'province': response.meta['province']}
                                 )


    #详情页面
    def parse_detail(self, response):
        item = {}
        #  #[UIID],[UIPhone] ,[UIName] ,[UIEmail] ,[UIPic],[UILawNumber],[LawOrg],[ProvinceCode],[CityCode],[Address],[UISignature]
        item["UIID"] = str(uuid.uuid1()).replace('-', '')
        uiphone =''.join(response.xpath('/html/body/div[1]/div[1]/div/div/div[2]/div[2]/text()').re('[^\s+]'))
        match_count = len(re.findall(r'[1][3,4,5,6,7,8][0-9]{9}', uiphone))
        item['UILawNumber'] = ''.join(response.xpath("/html/body/div[1]/div[1]/div/div/div[2]/div[3]/text()").re('[^\s+]'))
        if item["UILawNumber"] != None and len(item["UILawNumber"]) == 17 and self.userInfoInfoData.find_lawyer_by_lawlumber((item["UILawNumber"],)) == None :
            item["UIPhone"] = None if match_count == 0 else uiphone
            item['UIName'] = ''.join(response.xpath("/html/body/div[1]/div[1]/div/div/div[2]/div[1]/div[1]/text()").re('[^\s+]')).replace(u'律师','')
            item['LawOrg'] =''.join(response.xpath('/html/body/div[1]/div[1]/div/div/div[2]/div[4]/text()').re('[^\s+]'))
            item['UIEmail'] = None
            item["UISignature"]=''.join(response.css('#about::text').re('[^\s+]')).replace("\t",'')
            item["Address"] = ''.join(response.xpath('/html/body/div[1]/div[1]/div/div/div[2]/div[5]/text()').re('[^\s+]'))
            item["ProvinceCode"] = ''.join(self.areaData.find_area_by_name_return_code((response.meta['province'])))
            item["CityCode"]=None
            fiil_str = ''.join(response.xpath('/html/body/div[1]/div[1]/div/div/div[3]/span/text()').extract()).replace('\r','').replace('\t','').replace('\n','')
            item['fiil_str'] = field_info_dic.find_field_by_name(fiil_str.split(" "))
            # 头像路径
            dirname='fws'
            head_url = ''.join(response.css('.lshil3-1-1 img::attr(src)').extract())
            item["UIPic"] = ''.join(http_util.downloadImage([head_url], '/AppFile/' + dirname + "/" + item["UIID"] + '/head'))
            if item["UIPic"]=='' or item["UIPic"]==None:
               item["UIPic"]='/APPFile/head.jpg'
            item['url'] = response.url
            return item



    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)