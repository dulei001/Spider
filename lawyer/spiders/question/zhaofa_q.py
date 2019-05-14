#!/usr/bin/python
#-*- coding: utf-8 -*-

import uuid
import scrapy
from dal.service.AreaData import AreaData
from dal.service.QuestionData import QuestionData
from lawyer.spiders.lawers.field_info_dic import field_info_dic

class ZhaoFaQuestionSpider(scrapy.Spider):
    name = "zhaofa_q"
    start_urls = ["http://china.findlaw.cn"]
    areaData = AreaData()
    duestionData = QuestionData()

    def parse(self, response):
           list_url='http://china.findlaw.cn/ask/browse_t01_page{0}/'
           for p in range(1,7747):
               yield scrapy.Request(url=list_url.format(str(p)), callback=self.parse_question_next_page, errback=self.handle_error)


    def parse_question_next_page(self,response):
            for li in response.css(".result-list li"):
                fieldname=''.join(li.css('.rli-item.item-classify::text').extract())
                detail_url=li.css("a::attr(href)").extract_first()
                yield  scrapy.Request(url=detail_url,meta={'fieldname': fieldname},
                                                    callback=self.parse_detail,
                                                    errback=self.handle_error)



    def parse_detail(self, response):
        item={}
        item["Content"] = ''.join(response.css('.q-title::text').extract()).replace(' ','')
        if item["Content"]!='':
            item["ID"] = str(uuid.uuid1()).replace('-', '')
            item["UserName"]= ''.join(response.xpath('//p[@class="q-about"]/span[1]/text()').extract()).replace(' ','').replace(u"提问者：",'')
            item["CreateTime"] = ''.join(response.xpath('//p[@class="q-about"]/span[2]/text()').extract()).replace( u"时间：", '')
            item["UserHeadUrl"] = '/APPFile/userhead.jpg'
            province= ''.join(response.xpath("//div[@class='site-location']/a[3]/text()").extract()).replace(' ','').replace(u"法律咨询",'')
            city = ''.join(response.xpath("//div[@class='site-location']/a[4]/text()").extract()).replace(' ','').replace( u"法律咨询", '')
            item["ProvinceCode"] = None
            item["CityCode"] = None
            if(province!=None):
                prodata=self.areaData.find_area_by_name_return_code((province))
                if prodata!=None:
                    item["ProvinceCode"] = ''.join(prodata)
            if (city != None):
                citydata= self.areaData.find_area_by_name_return_code((city))
                if citydata!=None:
                    item["CityCode"] = ''.join(citydata)
            fiildstr = field_info_dic.find_field_by_name([response.meta['fieldname']])
            item['FIID']=None
            if len(fiildstr)>0:
                item['FIID']=fiildstr[0]
            item["url"]=response.url
        #ID,UserName,UserHeadUrl,Content,CreateTime,ProvinceCode,CityCode,FIID
            self.duestionData.insert_free_question((item["ID"] ,
                                                    item["UserName"],
                                                    item["UserHeadUrl"],
                                                    item["Content"],
                                                    item["CreateTime"],
                                                    item["ProvinceCode"],
                                                    item["CityCode"],
                                                    item["FIID"],
                                                     ))

            item['Replys']=[]
            for  r in  response.xpath('//div[@class="answer"]'):
                  reply={}
                  reply["ID"] = str(uuid.uuid1()).replace('-', '')
                  reply['Content']=r.css('.about-text::text').extract_first()
                  reply['CreateTime'] = r.css('.an-time::text').extract_first()
                  # UIID 暂时为空，导入完成数据库指定律小脉 ：e40b0d4f5bdc4732a3bdc8c66d4269c3
                  #ID,UIID,Content,QID,RID,CreateTime,IsDel
                  reply['UIID']=None
                  reply['RID']=None
                  reply['QID']=item["ID"]
                  reply['IsDel'] = 0
                  item['Replys'].append(reply)
                  self.duestionData.insert_free_reply((reply["ID"],reply['UIID'],reply['Content'],reply['QID'],reply['RID'],reply['CreateTime'],reply['IsDel']))
            print  item

    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)
