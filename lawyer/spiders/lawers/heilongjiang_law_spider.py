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
#黑龙江律师抓取
class HeiLongJiangLawyerSpider(scrapy.Spider):
    name = "hlj_law_spider"
    start_urls = ["http://hl.12348.gov.cn/gfpt/public/gfpt/ggflfw/wsbs/ls/tolist?dqbm=23"]
    areaData = AreaData()
    userInfoInfoData= UserInfoInfoData()
    pagesize=20
    provincode='23'
    baseurl = "http://hl.12348.gov.cn/gfpt/public/gfpt/ggflfw/wsbs/ls/listlsry"

    def parse(self, response):
        for item in  response.css("#shiqu_second li a::attr(onclick)").extract():
            prostr = item.split(u',')
            citycode =prostr[0].replace(u'xzShi(','').replace(u"'",'')
            cityname = prostr[1].replace(u"'",'')
            yield scrapy.FormRequest(url=self.baseurl,
                                     method="POST",
                                     headers={'X-Requested-With': 'XMLHttpRequest'},
                                     dont_filter=True,
                                     callback=self.parseAjaxPageList,
                                     errback=self.handle_error,
                                     meta={'citycode':citycode,'cityname':cityname},
                                     formdata={ "dqPage":'1','countSize':str(self.pagesize),'startSize':'1','dqbm':citycode,'type':'1','rymc':u'请输入关键词'}
                                     )

    def parseAjaxPageList(self,response):
        yieldlist=[]
        data = json.loads(response.body_as_unicode())
        pagecount = int(data['countPage'])
        yieldlist.extend(self.parseAjaxList(response))
        for page  in range(2,pagecount):
            countSize=self.pagesize*page
            startSize=self.pagesize+page
            yieldlist.append(scrapy.FormRequest(url=self.baseurl,
                                     method="POST",
                                     headers={'X-Requested-With': 'XMLHttpRequest'},
                                     dont_filter=True,
                                     callback=self.parseAjaxList,
                                     errback=self.handle_error,
                                     meta={'citycode': response.meta['citycode'], 'cityname': response.meta['cityname']},
                                     formdata={"dqPage": str(page), 'countSize':str(countSize),'startSize':str(startSize), 'dqbm':response.meta['citycode'],'type':'1','rymc':u'请输入关键词'}))
        return  yieldlist



    def parseAjaxList(self,response):
        data = json.loads(response.body_as_unicode())
        detail_url='http://hl.12348.gov.cn/gfpt/public/gfpt/ggflfw/wsbs/ls/ryDetail?rybm={0}'
        for item in data['lsrylist']:
            yield  scrapy.Request(url=detail_url.format(item[0]),method="GET", dont_filter=True, meta={ 'cityname': response.meta['cityname']}, errback=self.handle_error,callback=self.parse_detail,)

    #详情页面
    def parse_detail(self, response):
        item = {}
        #  #[UIID],[UIPhone] ,[UIName] ,[UIEmail] ,[UIPic],[UILawNumber],[LawOrg],[ProvinceCode],[CityCode],[Address],[UISignature]
        print  response.url
        item["UIID"] = str(uuid.uuid1()).replace('-', '')
        uiphone =''.join(response.xpath('/html/body/div[2]/div/div[3]/div/dl/dd/li[6]/text()').re('[^s]')).replace(' ','').replace('\t','').replace('\n','')
        match_count = len(re.findall(r'[1][3,4,5,6,7,8][0-9]{9}', uiphone))
        item['UILawNumber'] = ''.join(response.xpath('/html/body/div[2]/div/div[3]/div/dl/dd/li[3]/text()').re('[^s]')).replace(' ','').replace('\t','').replace('\n','')
        if item["UILawNumber"] != None and len(item["UILawNumber"]) == 17 and self.userInfoInfoData.find_lawyer_by_lawlumber((item["UILawNumber"],)) == None :
            item["UIPhone"] = None if match_count == 0 else uiphone
            item['UIName'] = ''.join(response.xpath('/html/body/div[2]/div/div[3]/div/dl/dd/h1/text()').re('[^s]')).replace(' ','').replace('\t','').replace('\n','')
            item["ProvinceCode"] = self.provincode
            item['LawOrg'] =  ''.join(response.xpath('/html/body/div[2]/div/div[3]/div/dl/dd/li[4]/a/text()').re('[^s]')).replace(' ','').replace('\t','').replace('\n','')
            item['UIEmail'] =None
            item["UISignature"]=''.join(response.xpath('//*[@id="news_content_0"]/text()').re('[^s]')).replace(' ','').replace('\t','').replace('\n','').replace('\r','')
            item["Address"] = None
            item["CityCode"] = ''.join(self.areaData.find_area_by_name_return_code((response.meta['cityname'])))
            # 头像路径
            dirname='hlj'
            headurl=response.xpath('/html/body/div[2]/div/div[3]/div/dl/dt/img/@src').extract_first()
            item["UIPic"] = ''.join(http_util.downloadImage(["http://hl.12348.gov.cn" + headurl], '/AppFile/'+ dirname+"/"+ item["UIID"] + '/head'))
            item['url'] = response.url
            return item



    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)