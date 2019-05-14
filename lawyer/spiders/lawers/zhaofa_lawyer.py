#!/usr/bin/python
#-*- coding: utf-8 -*-
import json
import re
import uuid

import requests
import scrapy

from dal.service.AreaData import AreaData
from dal.service.UserInfoInfoData import UserInfoInfoData
from lawyer import http_util
from lawyer.spiders.lawers.field_info_dic import field_info_dic

class ZhaoFaLawyerSpider(scrapy.Spider):
    name = "zhaofa_lawyer"
    start_urls = ["http://china.findlaw.cn/beijing/lawyer"]
    areaData = AreaData()
    userInfoInfoData= UserInfoInfoData()


    def parse(self, response):
       provinceSet=list()
       urlmetedata=list()
       child_city_url='http://china.findlaw.cn/area_front/index.php?c=ajax&a=getChildCity'
       headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
       for item in  response.xpath("//select[@id='province']/option/@value").extract():
           if item!='':
             provinceSet.append(item)
       for pro in provinceSet:
           res = requests.post(child_city_url, data={'areacode': pro,'profPy':None,'typeid':'0'},headers=headers)
           data =  res.json()
           for key in  data['data']:
               try:
                   urlmetedata.append({'url': data['data'][key]['url'], 'province': data['data'][key]['province'],
                                       'city': data['data'][key]['city']})
               except Exception as e:
                   pass
       for item in urlmetedata:
           yield scrapy.Request(url=item['url'],meta={'province': item['province'],'city':item['city']},
                                callback=self.parse_lawyer_next_page,
                                errback=self.handle_error)



    def parse_lawyer_next_page(self,response):
        last_page_url=''.join(response.xpath("//div[@class='common-pagination']/a[last()]/@href").extract())
        self.parse_lawyer_list(response)
        if last_page_url !='':
            pagecount = int(re.match('.*/p_(?P<page>\d+)/', last_page_url).group('page'))
            for page in range(2,int(pagecount)):
                list_url= response.url+'/p_'+str(page)
                yield  scrapy.Request(url=list_url,meta={'province': response.meta['province'],'city': response.meta['city']},
                                                    callback=self.parse_lawyer_list,
                                                    errback=self.handle_error)

    def parse_lawyer_list(self, response):
        for item in response.css(".sr-list li"):
            detail_url= item.css(".lawyer_name::attr(href)").extract_first()
            yield scrapy.Request(url=detail_url,
                                     meta={'province': response.meta['province'], 'city': response.meta['city']},
                                     callback=self.parse_lawyer_item,
                                     errback=self.handle_error)



    def parse_lawyer_item(self, response):
        item={}
        zhiye = response.xpath("//dl[@class='information_practice information_practice_new']")
       # print ''.join(zhiye.extract())
        item["UILawNumber"] = ''.join(zhiye.xpath(u'dd/span[contains(text(),"律师证编号：")]/text()').extract()).replace(u'执业律师 (律师证编号：', '').replace(u')', '').replace(' ','')
        uiphone = ''.join(response.css('.right_consult_phone a::text').extract())

        match_count = len(re.findall(r'[1][3,4,5,6,7,8][0-9]{9}', uiphone))
        item["UIPhone"] = None if match_count == 0 else uiphone
        #如果数据库不存在执业证号
        if item["UILawNumber"]!=None and len(item["UILawNumber"])==17 and self.userInfoInfoData.find_lawyer_by_lawlumber((item["UILawNumber"],))==None and item["UIPhone"]!=None:
            item["UIName"]= ''.join(response.xpath('//h1[@class="lvshi_info_name"]/text()').extract()).replace(' ','').replace(u"律师",'')
            item["LawOrg"] = response.xpath('//p[@class="lvshi_info_add"]/text()').extract_first()
            item["Address"] = ''.join(response.css('.information_practice_dd::text').extract()).replace(' ', '')
            item["UIEmail"] = None
            desc = ''.join(response.xpath("//p[@class='information_info']/span/text()").extract()).replace(u"\xa0",'')
            desc= re.sub(r'(<a.*?>.*?</a>)|((class|style|color|href)="[^"]*?")|(<.*?>)|(<[/].*?>)', '', desc).replace("\r",'').replace("\n",'').replace(' ','')
            item["UISignature"] = None if desc== ''else desc.replace(u"\xa0",'').replace("\t",'').replace("\n",'').replace(' ','').replace(u'&amp;','').replace('...','')
            item["ProvinceCode"] =''.join( self.areaData.find_area_by_name_return_code(( response.meta['province'])))
            item["CityCode"] = ''.join(self.areaData.find_area_by_name_return_code(( response.meta['city'])))
            item["UIID"]=  str(uuid.uuid1()).replace('-', '')
            item["UIPic"] = ''.join(http_util.downloadImage(["http:" + ''.join(response.css('.lvshi_info_pic a img::attr(src)').extract())], '/AppFile/'+item["UIID"]+'/head'))
            item["url"]=response.url
            return  item

    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)
