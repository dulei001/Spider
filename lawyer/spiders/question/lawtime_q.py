#!/usr/bin/python
#-*- coding: utf-8 -*-

import uuid

import re
import scrapy
from dal.service.AreaData import AreaData
from dal.service.QuestionData import QuestionData

class LawtimeQuestionSpider(scrapy.Spider):
    name = "lawtime_q"
    start_urls = ["http://www.lawtime.cn"]
    areaData = AreaData()
    duestionData = QuestionData()

    def parse(self, response):
           list_url='http://www.lawtime.cn/ask/browse_t2_p{0}.html'
           for p in range(3, 118):
               yield scrapy.Request(url=list_url.format(str(p)), callback=self.parse_question_next_page, errback=self.handle_error)


    def parse_question_next_page(self,response):
            for li in response.css(".tab-body li"):
                province_city=''.join(li.css(".info::text").extract())
                detail_url=li.css("a::attr(href)").extract_first()
                yield  scrapy.Request(url=detail_url,meta={'province_city': province_city},
                                                    callback=self.parse_detail,
                                                    errback=self.handle_error)



    def parse_detail(self, response):
        item={}
        province_city = response.meta['province_city'].split('-')
        title = ''.join(response.css('.title::text').extract()).replace(' ','').replace(u'最佳答案其他','')
        content = ''.join(response.css('.content::text').extract()).replace(' ', '').replace(u'最佳答案其他','')
        item["Content"]=content if content!='' else title
        if item["Content"]!='':
            item["ID"] = str(uuid.uuid1()).replace('-', '')
            qinfo=''.join(response.css('.question .info::text').extract())
            item["UserName"]= qinfo[0:qinfo.index(u'　')]
            item["CreateTime"] = qinfo[qinfo.index(('-')):].replace(u'\u3000','').lstrip('-')
            item["UserHeadUrl"] = '/APPFile/userhead.jpg'
            province= province_city[0].replace('[','')
            city = province_city[1].replace(']','')
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
            item['FIID']=None
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
            for  r in  response.xpath('//div[@class="answer-item"]'):
                  reply={}
                  reply["ID"] = str(uuid.uuid1()).replace('-', '')
                  reply['Content']= ''.join(r.css('.answer-w p:nth-child(1)::text').extract())
                  reply['CreateTime'] = ''.join(r.css('.time:nth-child(1)::text').extract())
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
