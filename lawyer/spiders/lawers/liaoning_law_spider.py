#!/usr/bin/python
#-*- coding: utf-8 -*-
import uuid

import re
import scrapy

from dal.service.AreaData import AreaData
from dal.service.UserInfoInfoData import UserInfoInfoData
from lawyer import http_util
from   lawyer.spiders.lawers.field_info_dic import field_info_dic
#辽宁律师抓取
class LiaoNingLawyerSpider(scrapy.Spider):
    name = "liaoning_law_spider"
    start_urls = ["http://218.60.145.124:8080/lnlxoa/govhall/lawyerResult.jsp"]
    areaData = AreaData()
    userInfoInfoData= UserInfoInfoData()
    def parse(self, response):
        baseurl = "http://218.60.145.124:8080/lnlxoa/govhall/lawyerResultOne.jsp?pn={0}"
        #1145
        for i in range(1, 1145):
            yield scrapy.Request(url=baseurl.format(str(i)), method="GET", callback=self.parse_list,
                                 meta={"dont_redirect": True}, errback=self.handle_error, )

    def parse_list(self,response):
        url='http://218.60.145.124:8080//lnlxoa/govhall/{0}'
        for i in response.css('.zi11 a::attr(href)'):
            yield scrapy.Request(url=url.format(i.extract()), method="GET", callback=self.parse_detail,
                                 meta={"dont_redirect": True}, errback=self.handle_error, )

    #详情页面
    def parse_detail(self, response):
        item = {}
        #  #[UIID],[UIPhone] ,[UIName] ,[UIEmail] ,[UIPic],[UILawNumber],[LawOrg],[ProvinceCode],[CityCode],[Address],[UISignature]
        item["UIID"] = str(uuid.uuid1()).replace('-', '')
        table = response.xpath('//div[@class="zi35"]/table')
        uiphone = "".join(table.xpath('tr[7]/td/text()').re('[^\s]')).split(u'：')[1]
        match_count = len(re.findall(r'[1][3,4,5,6,7,8][0-9]{9}', uiphone))
        item['UILawNumber'] = "".join(table.xpath('tr[11]/td[1]/text()').re('[^\s]')).split(u'：')[1]
        if item["UILawNumber"] != None and len(item["UILawNumber"]) == 17 and self.userInfoInfoData.find_lawyer_by_lawlumber((item["UILawNumber"],)) == None :
            item["UIPhone"] = None if match_count == 0 else uiphone
            item['UIName'] = "".join(table.xpath('tr[1]/td[1]/text()').re('[^\s]')).split(u'：')[1]
            item["ProvinceCode"] = ''.join(self.areaData.find_area_by_name_return_code((u'辽宁')))
            item['LawOrg'] = "".join(table.xpath('tr[2]/td/text()').re('[^\s]')).split(u'：')[1]
            item['UIEmail'] = "".join(table.xpath('tr[14]/td/text()').re('[^\s]')).split(':')[1]
            item["UISignature"]=None
            item['FIID'] = None
            item["Address"] =None
            item["CityCode"] =None
            # 头像路径
            dirname='liaoning'
            item["UIPic"] = ''.join(http_util.downloadImage(["http://218.60.145.124:8080/lnlxoa/govhall" + "".join(table.xpath('tr[1]/td[2]/img/@src').re('[^\s]'))], '/AppFile/'+ dirname+"/"+ item["UIID"] + '/head'))
            item['url'] = response.url
            return item



    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)