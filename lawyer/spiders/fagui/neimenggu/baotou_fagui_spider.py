#!/usr/bin/python
#-*- coding: utf-8 -*-
import re
import uuid
import scrapy
class baotouSpider(scrapy.Spider):
    """包头市"""
    name = "baotou"
    provinceName=u"内蒙古"
    cityName=u"包头市"
    provinceCode="15"
    cityCode = "1503"
    level=u"地方法规"
    start_urls = [
        'http://www.baotou.gov.cn',
        ]
    page_domain = 'http://www.baotou.gov.cn%s'
    fagui_statr_arr=[
        {"name":u"通知", "url":"http://www.baotou.gov.cn/01xxgk/xxgk_list_bmml.jsp?ainfolist2326t=94&ainfolist2326p={0}&ainfolist2326c=15&urltype=egovinfo.EgovCustomURl&wbtreeid=1578&type=deptsubcattree&dpcode=szfbgt&dpopenitem=szfbgt","page":94},
    ]

    def parse(self, response):
        for item in self.fagui_statr_arr:
             for pages in range(1,int(item["page"])):
                  yield  scrapy.Request(str(item["url"]).format(str(pages)), callback=self.parse_page_list, method='get',
                                                errback=self.handle_error,meta={'stype':item["name"]})

    def parse_page_list(self,response):
        for item in response.xpath("//div[@class='govinfolist2326']/table/tr/td[1]/a"):
            detailbaseurl=  self.page_domain % ''.join(item.css("::attr(href)").extract()).replace('..','')
            yield scrapy.Request(detailbaseurl, callback=self.parse_detail, method='get',dont_filter=True,
                                 errback=self.handle_error, meta={'stype': response.meta["stype"]})

    def parse_detail(self,response):
        item = {}
        bodyhtml=response.css(".xxgk_listbiaoge01/*").xpath("table[1]/tr[1]/td[1]/table")
        title = ''.join(bodyhtml.xpath("tr[1]/td[1]/text()").re('[^\s+]'))
        if  title!='':
           item['title'] = title
           item['anNo']=''.join(bodyhtml.xpath("tr[2]/td[1]/table/tr[2]/td[6]/text()").re('[^\s+]'))
           item['pubish_time'] =''.join(bodyhtml.xpath("tr[2]/td[1]/table/tr[1]/td[6]/text()").re('[^\s+]')).replace(u"年","-").replace(u"月","-").replace(u"日","")
           item['effect_time'] = None
           item['pubish_org'] = ''.join(bodyhtml.xpath("tr[2]/td[1]/table/tr[2]/td[4]/text()").re('[^\s+]'))
           item['level']= self.level
           item['time_liness'] = u"现行有效"
           content =  ''.join(response.css('#vsb_content_2').extract())
           if content=='':
               content = ''.join(response.css('#vsb_content').extract())
           item["content"] =re.sub('((id|class|style|color|href|target|align|title)="[^"]*?")|(<img .*?>)', '', content).replace('<?xml:namespace prefix="o" ns="urn:schemas-microsoft-com:office:office" />','')  # 内容'''
           item['url'] = response.url
           item["provinceName"]=self.provinceName
           item["cityName"]=self.cityName
           item["provinceCode"] = self.provinceCode
           item["cityCode"] = self.cityCode
           item['sIndex'] = ''.join(bodyhtml.xpath("tr[2]/td[1]/table/tr[1]/td[2]/text()").re('[^\s+]'))
           item["sTypeName"]=response.meta["stype"]
           item['source'] = u"包头市人民政府"
           # 是否导入正式数据库
           item['export'] = '0'
           item['collection'] = 'fagui'
           item["Id"]=str(uuid.uuid1()).replace('-', '')
           return  item



    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)


