#!/usr/bin/python
#-*- coding: utf-8 -*-

import uuid

import re
import scrapy
from dal.service.AreaData import AreaData
from dal.service.QuestionData import QuestionData
from lawyer.spiders.lawers.field_info_dic import field_info_dic
class FaBangQuestionSpider(scrapy.Spider):
    name = "fabang_q"
    start_urls = ["http://www.fabang.com"]
    areaData = AreaData()
    duestionData = QuestionData()

    def parse(self, response):
           list_url='http://www.fabang.com/ask/browser_0_0_0_0_3_{0}.html'
           for p in range(1, 4682):
               yield scrapy.Request(url=list_url.format(str(p)), callback=self.parse_question_next_page, errback=self.handle_error)


    def parse_question_next_page(self,response):
            for li in response.css(".list ul li"):
                province_city=''.join(li.css("span:nth-child(3)::text").extract())
                fieldname = ''.join(li.css('.tit::text').extract()).replace(u'\u3000','').replace('[','').replace(']','').replace(' ', '').replace('\n','').replace('\t','').replace('\r','')
                detail_url= 'http://www.fabang.com/ask/'+li.css(".tit a::attr(href)").extract_first()
                yield  scrapy.Request(url=detail_url,meta={'province_city': province_city,'fieldname':fieldname},
                                                    callback=self.parse_detail,
                                                    errback=self.handle_error)



    def parse_detail(self, response):
        item={}
        province_city = response.meta['province_city'].split('-')
        item["Content"] = response.xpath('//div[@class="tbrig"][1]/p[1]/text()').extract()[0].replace(' ', '').replace('\n','').replace('\t','')
        if item["Content"]!='':
            item["ID"] = str(uuid.uuid1()).replace('-', '')
            item["UserName"]= response.xpath('//div[@class="tblef"][1]/span[@class="username color06b"]/a/text()').extract()[0].replace(u'\u3000','').replace(' ','')
            item["CreateTime"] = ''.join(response.css('.fenxiang.margintop10 b::text').extract())
            item["UserHeadUrl"] = '/APPFile/userhead.jpg'
            province= province_city[0]
            city = province_city[1]
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
            item['FIID'] = None
            if len(fiildstr) > 0:
                item['FIID'] = fiildstr[0]
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
            isfilter=0;
            for  r in response.xpath('//div[@class="tbrig"]'):
                  if isfilter==0:
                      isfilter = 1
                      continue;
                  reply={}
                  reply["ID"] = str(uuid.uuid1()).replace('-', '')
                  reply['Content']= ''.join(r.xpath('p[1]/text()').extract()).replace(' ', '').replace('\n','').replace('\t','')
                  ftime=''.join(r.xpath('span[1]/label[1]/b[1]/text()').extract()).replace('\n','').replace('\t','')
                  stime = ''.join(r.xpath('span[1]/b[1]/text()').extract()).replace('\n', '').replace('\t', '')
                  reply['CreateTime'] = ftime if ftime!='' else stime
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
