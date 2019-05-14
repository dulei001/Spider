#!/usr/bin/python
#-*- coding: utf-8 -*-
import re
import uuid

import scrapy

from dal.service.AreaData import AreaData
from dal.service.UserInfoInfoData import UserInfoInfoData
from lawyer import http_util
from   lawyer.spiders.lawers.field_info_dic import field_info_dic

class FabangLawyerSpider(scrapy.Spider):
    name = "fabang_lawyer"
    start_urls = ["http://lawyer.fabang.com"]
    areaData = AreaData()
    userInfoInfoData= UserInfoInfoData()
    def parse(self, response):
        start_url="http://lawyer.fabang.com/list/0-0-0-key-1-{0}.html"
        for page in range(1,1075):
            yield scrapy.Request(url=start_url.format(str(page)),
                           method="get",
                           callback=self.parse_lawyer_list,
                           errback=self.handle_error)

    def parse_lawyer_list(self,response):
        for detail_html in response.css(".lawyerlist"):
            detail_url= detail_html.css(".uname::attr(href)").extract_first()
            yield  scrapy.Request(url=detail_url,
                                                callback=self.parse_lawyer_item,
                                                errback=self.handle_error)



    def parse_lawyer_item(self, response):
        item={}
        item["UILawNumber"] = ''.join(response.xpath(u'//p[contains(text(),"执业证号：")]/text()').extract()).replace(' ','').replace(u'执业证号：', '')
        uiphone = ''.join(response.xpath('//strong[@class="mobile"]/text()').extract()).replace(' ', '')
        match_count = len(re.findall(r'[1][3,4,5,6,7,8][0-9]{9}', uiphone))
        item["UIPhone"] = None if match_count == 0 else uiphone
        #如果数据库不存在执业证号
        if item["UILawNumber"]!=None and len(item["UILawNumber"])==17 and self.userInfoInfoData.find_lawyer_by_lawlumber((item["UILawNumber"],))==None and item["UIPhone"]!=no:
            item["UIName"]= ''.join(response.xpath('//strong[@class="lawyername"]/text()').extract()).replace(' ','').replace(u"律师",'')

            item["LawOrg"] = response.xpath('//p[@class="jigou"][1]/a/text()').extract_first()
            item["Address"] = ''.join(response.xpath(u'//p[contains(text(),"地\xa0\xa0\xa0\xa0址：")]/text()').extract()).replace(' ', '').replace( u'地\xa0\xa0\xa0\xa0址：', '')
            item["UIEmail"] = ''.join(response.xpath(u'//p[contains(text(),"邮\xa0\xa0\xa0\xa0箱：")]/text()').extract()).replace(' ','').replace(u'邮\xa0\xa0\xa0\xa0箱：', '')
            fiil_str = ''.join(response.xpath(u'//p[contains(text(),"专长领域：")]/text()').extract()).replace(' ', '').replace( u'专长领域：', '')
            desc = ''.join(response.xpath("//div[@class='content'][last()]/*").extract()).replace(u"\xa0",'')
            desc= re.sub(r'(<a.*?>.*?</a>)|((class|style|color|href)="[^"]*?")|(<.*?>)|(<[/].*?>)', '', desc).replace("\r",'').replace("\n",'').replace(' ','')
            s_start_index=0 if desc.index(u'分享到：')==-1 else  desc.index(u'分享到：')
            item["UISignature"] = None if desc== ''else desc[s_start_index:].replace( u'分享到：', '').replace(u"\xa0",'').replace("\t",'').replace("\n",'').replace(' ','').replace(u'&amp;','').replace('...','')
            province_city=response.xpath('//div[@class="info_nm SG_txtc "]/text()').extract_first().replace("\r", '').replace("\n", '').split(" ")
            item["ProvinceCode"] =''.join( self.areaData.find_area_by_name_return_code((province_city[0])))
            item["CityCode"] = ''.join(self.areaData.find_area_by_name_return_code((province_city[1])))
            item['fiil_str'] = field_info_dic.find_field_by_name(fiil_str.split(u"\xa0"))
            item["UIID"]=  str(uuid.uuid1()).replace('-', '')
            item["UIPic"] = ''.join(http_util.downloadImage(["http://lawyer.fabang.com" + ''.join(response.css('.info_img_area img::attr(src)').extract())], '/AppFile/'+item["UIID"]+'/head'))
            item["url"]=response.url
            return item

    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)
