#!/usr/bin/python
#-*- coding: utf-8 -*-
import re
import uuid

import scrapy
from pymongo import MongoClient

from devops import scrapyd_cencel
from devops import scrapyd_deploy
from devops import scrapyd_scheduling
from datetime import  datetime
from  dal.service.StatuteData import StatuteData
class qfayuan_fagui_spider(scrapy.Spider):
    """中国法院网法规"""

    name = "qfyfagui"
    statuteData = StatuteData()
    allowed_domains=["www.chinacourt.org"]

    start_urls = [
        'http://www.chinacourt.org/law/more/law_type_id/MzAwNEAFAA%3D%3D/page/1.shtml',  # 国家法规库
        'https://www.chinacourt.org/law/more/law_type_id/MzAwM0AFAA%3D%3D/page/1.shtml',  # 司法解释
        'https://www.chinacourt.org/law/more/law_type_id/MzAwMkAFAA%3D%3D/page/1.shtml',  # 地方法规
        'https://www.chinacourt.org/law/more/law_type_id/MzAwMUAFAA%3D%3D/page/1.shtml'  # 政策参考
        ]
    page_domain = "http://www.chinacourt.org%s"



    def parse(self, response):
        self.parse_list(response)
        pageurlstr= ''.join(response.xpath(u'//a[text()="尾页"]/@href').extract())
        pagecount= int(re.match('.*/page/(?P<page>\d+)\.shtml', pageurlstr).group('page'))
        for page in range(2,pagecount):
            pageurl = re.sub(r'(?P<page>\d+)\.shtml', '{0}.shtml'.format(str(page)), response.url)
            yield scrapy.Request(pageurl, callback=self.parse_list, method='get', errback=self.handle_error)


    def parse_list(self,response):
        for item in response.xpath('//div[@class="law_list"]')[0].css("ul li"):
            detailurl = item.css('.left a::attr(href)').extract_first()
            title=item.css('.left a::text').extract_first()
            detail_url = self.page_domain % detailurl
            yield   scrapy.Request(detail_url, callback=self.parse_detail, method='get',
                                                errback=self.handle_error,meta={"title":title})


    def parse_detail(self,response):
        item = {}
        item['title'] = response.meta['title']
        if response.css(" .STitle")!=None:
           STitle = "".join(response.css(".law_content .STitle").re('[^\s]')).split("<br>")
           item['anNo']=''
           item['pubish_time'] = None
           item['effect_time'] = None
           item['pubish_org'] = ''
           item['level']=''
           for st in STitle:
               sindex=st.find(u"】")+1
               if st.find(u"发布文号") != -1:
                  # 发文字号
                  item['anNo'] = st[sindex:len(st)]
               if st.find(u"发布日期") != -1:
                  # 颁布日期
                  item['pubish_time'] = st[sindex:len(st)]

               if st.find(u"生效日期") != -1:
                  # 生效日期
                  item['effect_time'] =st[sindex:len(st)]

                  # 颁布机构
               if st.find(u"发布单位") != -1:
                  item['pubish_org'] = st[sindex:len(st)]

               # 效力级别
               if st.find(u"所属类别") != -1:
                  item['level'] = st[sindex:len(st)]
           # 时效性
           item['time_liness'] = ""
           content = ''.join(response.css('.content_text').extract())
           item["content"] = re.sub('(class|style|color|href)="[^"]*?"', '', content)  # 内容'''
           item['url'] = response.url
           item['source'] = u"中国法院网"
           # 是否导入正式数据库
           item['export'] = '0'
           item['collection'] = 'fagui'
           uid=str(uuid.uuid1()).replace('-', '')
           #Id,Time_liness,Effect_time,Level,Pubish_time,Title,AnNo,Source,Pubish_org,Content,IsBuild
           self.statuteData.insert_statute((uid,u'',item['effect_time'],item['level'],item['pubish_time'],item['title'],item['anNo'],item['source'],item['pubish_org'],item["content"],0))
           del  item["content"]
           print item



    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)




