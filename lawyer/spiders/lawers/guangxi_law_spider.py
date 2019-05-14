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
#广西律师抓取
class ShanDongLawyerSpider(scrapy.Spider):
    name = "guangxi_law_spider"
    start_urls = ["http://gx.12348.gov.cn/lssws/index.jhtml"]
    areaData = AreaData()
    userInfoInfoData= UserInfoInfoData()
    pagesize=20
    provincode='45'
    baseurl = "http://gx.12348.gov.cn/lssws/index_1.jhtml?qkey=mscms.ms.getLSList&args_code={0}"
    def parse(self, response):
        isflag=0
        for item in  response.css(".content-inquiry-city button"):
            if isflag==0:
                isflag=1
                continue
            citycode = item.xpath("@q").extract_first()[0:4]
            cityname = item.xpath("text()").extract_first()
            city_href=self.baseurl.format(citycode)
            yield scrapy.FormRequest(url=city_href,
                                     method="GET",
                                     dont_filter=True,
                                     callback=self.parsePageList,
                                     errback=self.handle_error,
                                     meta={'cityname':cityname,'citycode':citycode},
                                     )

    def parsePageList(self,response):
        pagecountstr = response.css('#totalnum::attr(value)').extract_first()
        pagecount = (int(pagecountstr) - 1) / (self.pagesize + 1)
        page_next_url = "http://gx.12348.gov.cn/lssws/index_{0}.jhtml?qkey=mscms.ms.getLSList&args_code={1}"
        for page  in range(1,pagecount):
            yield scrapy.FormRequest(url=page_next_url.format(str(page),response.meta['citycode']),
                                     method="GET",
                                     dont_filter=True,
                                     callback=self.parseList,
                                     errback=self.handle_error,
                                     meta=response.meta,
                                     )



    def parseList(self,response):
        for item in response.css('.search-results-box a::attr(href)').extract():
            detail_url =  "http://gx.12348.gov.cn"+item.replace('..','')
            yield scrapy.FormRequest(url=detail_url,
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
        uiphone = response.css('.zynx::text').extract_first().replace('\t','').replace('\r','').replace('\n','')
        match_count = len(re.findall(r'[1][3,4,5,6,7,8][0-9]{9}', uiphone))
        item['UILawNumber'] = response.css('.zyzh::text').extract_first().replace('\t','').replace('\r','').replace('\n','')
        if item["UILawNumber"] != None and len(item["UILawNumber"]) == 17 and self.userInfoInfoData.find_lawyer_by_lawlumber((item["UILawNumber"],)) == None :
            item["UIPhone"] = None if match_count == 0 else uiphone
            item['UIName'] = response.xpath("//div[@class='row ryjs-top-name']/h3/text()").extract_first().replace('\t','').replace('\r','').replace('\n','')
            item["ProvinceCode"] = self.provincode
            item['LawOrg'] =  response.css(".zyjg a::text").extract_first().replace('\t','').replace('\r','').replace('\n','')
            item['UIEmail'] =None
            item["UISignature"]=None
            item['fiil_str'] = field_info_dic.find_field_by_name(''.join(response.css("#ywzc::attr(value)").extract()).split(u","))
            item["Address"] = response.xpath("/html/body/div[1]/div[4]/div/div[2]/div[2]/div[1]/div[5]/span/text()").extract_first().replace('\t','').replace('\r','').replace('\n','')
            item["CityCode"] = ''.join(self.areaData.find_area_by_name_return_code((response.meta['cityname'])))
            # 头像路径
            dirname='guangxi'
            headurl= "http://gx.12348.gov.cn"+ ''.join(response.xpath('//img[@id="img-billid"]/@src').extract()).replace('..','')
            item["UIPic"] = ''.join(http_util.downloadImage([headurl], '/AppFile/'+ dirname+"/"+ item["UIID"] + '/head'))
            item['url'] = response.url
            return item



    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)