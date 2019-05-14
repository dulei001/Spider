#!/usr/bin/python
#-*- coding: utf-8 -*-
import uuid
import re
import scrapy
from dal.service.AreaData import AreaData
from dal.service.UserInfoInfoData import UserInfoInfoData
from   lawyer.spiders.lawers.field_info_dic import field_info_dic

class NeiMengGuSpider(scrapy.Spider):
    name = "neimenggu_law_spider"
    start_urls = ["http://110.16.70.5/fwsf_shfwh/lsList/1//////.html#abc"]
    areaData = AreaData()
    userInfoInfoData = UserInfoInfoData()
    provincode = '15'
    def parse(self, response):
        self.parse_list(response)
        for num in range(2, 409):
            url_detail = 'http://110.16.70.5/fwsf_shfwh/lsList/{0}//////.html#abc'.format((str(num)))
            yield scrapy.Request(url=url_detail,
                                 method='GET',
                                 dont_filter=True,
                                 callback=self.parse_list,
                                 errback=self.handle_error)

    def parse_list(self,response):
        for detail_path in response.xpath('/html/body/div[4]/div[2]/div/div/table[2]/tbody/tr[position()>1]'):
             detail_url= "http://110.16.70.5"+''.join(detail_path.xpath('td/a/@href').extract())
             yield scrapy.Request(url=detail_url,
                                       callback=self.parse_detail,
                                       errback=self.handle_error)


    def parse_detail(self,response):
        item={}
        item['UILawNumber'] ="".join(response.xpath('//*[@id="xzfyform"]/table/tbody/tr[4]/td[2]/text()').extract())
        uiphone = ''.join(response.xpath('//*[@id="xzfyform"]/table/tbody/tr[5]/td[2]/text()').extract())
        match_count = len(re.findall(r'[1][3,4,5,6,7,8][0-9]{9}', uiphone))
        if item["UILawNumber"] != None and len(item["UILawNumber"]) == 17 and self.userInfoInfoData.find_lawyer_by_lawlumber((item["UILawNumber"],)) == None and match_count!=0:
            item["UIID"] = str(uuid.uuid1()).replace('-', '')
            item["UIName"] = "".join(response.xpath('//*[@id="xzfyform"]/table/tbody/tr[1]/td[1]/text()').extract())
            # 性别
            sex = "".join(response.xpath('//*[@id="xzfyform"]/table/tbody/tr[1]/td[2]/text()').extract())
            item["UISex"] = None
            if (sex == u"男"):
                item["UISex"] = 0
            elif (sex == u"女"):
                item["UISex"] = 1
            item["UIPhone"] =uiphone
            item["ProvinceCode"] = self.provincode
            item['LawOrg'] = ''.join(response.xpath('//*[@id="xzfyform"]/table/tbody/tr[6]/td[2]/text()').extract())
            item['UIEmail'] =''.join(response.xpath( '//*[@id="xzfyform"]/table/tbody/tr[5]/td[1]/text()').extract())
            item["UISignature"] = None
            item["Address"] = ''.join(response.xpath( '//*[@id="xzfyform"]/table/tbody/tr[7]/td/text()').extract())
            item["CityCode"] = None
            fiil_str =  ''.join(response.xpath('//*[@id="xzfyform"]/table/tbody/tr[8]/td/text()/text()').extract()).replace(' ','').replace('\n','').replace('\r','')
            if fiil_str != None:
                item['fiil_str'] = field_info_dic.find_field_by_name(fiil_str.split(u","))
            item["UIPic"] = None
            return item
            return item

    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)


