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
class WYFGSpider(scrapy.Spider):
    """中国法院网法规"""

    name = "fyfagui"
    statuteData = StatuteData()
    allowed_domains=["www.chinacourt.org"]
    #抓取法规最后发布时间
    last_faguis=[
                    {'source':u'地方法规','pubish_time': '1950-03-29'},
                    {'source':u'国家法律法规', 'pubish_time':'1949-09-29'},
                    {'source':u'司法解释', 'pubish_time':'2011-03-01'},
                    {'source':u'政策参考', 'pubish_time':'1987-05-31'}
                 ]

    start_urls = [
        'http://www.chinacourt.org/law/more/law_type_id/MzAwNEAFAA%3D%3D/page/1.shtml', #国家法规库
        'https://www.chinacourt.org/law/more/law_type_id/MzAwM0AFAA%3D%3D/page/1.shtml', #司法解释
        'https://www.chinacourt.org/law/more/law_type_id/MzAwMkAFAA%3D%3D/page/1.shtml',#地方法规
        'https://www.chinacourt.org/law/more/law_type_id/MzAwMUAFAA%3D%3D/page/1.shtml'#政策参考
        ]
    page_domain = "http://www.chinacourt.org%s"


    def find_last_faguis(self,source,pub_time):
       hax_next = 1
       for item in  self.last_faguis:
           if item['source'] == source and datetime.strptime(item['pubish_time'], "%Y-%m-%d") < datetime.strptime(pub_time, "%Y-%m-%d"):
              hax_next = 0
              break
       return  hax_next

    def find_spider_max_fagui(self,response):
        hax_next = 1
        source = response.xpath('//div[@id="title"]/text()').extract_first()
        for item in response.xpath('//div[@class="law_list"]')[0].css("ul li").css('.right::text').extract():
            hax_next = self.find_last_faguis(source,item)
            if hax_next == 1:
                break
        return  hax_next


    def parse(self, response):
       page_list = []
       page_list.extend(self.parse_list(response))
       if self.find_spider_max_fagui(response) == 0:
           pageIndex = int(re.match('.*/page/(?P<page>\d+)\.shtml', response.url).group('page'))
           if response.xpath(u'//a[text()="下一页"]')!=None:
               pageurl = re.sub(r'(?P<page>\d+)\.shtml', '{0}.shtml'.format(str(pageIndex+1)), response.url)
               page_list.append(scrapy.Request(pageurl,callback=self.parse,method='get',errback=self.handle_error))
       return page_list


    def parse_list(self,response):
        page_list = []
        source = response.xpath('//div[@id="title"]/text()').extract_first()
        for item in response.xpath('//div[@class="law_list"]')[0].css("ul li"):
            detailurl = item.css('.left a::attr(href)').extract_first()
            if self.find_last_faguis(source,''.join(item.xpath('span[2]/text()').extract()))==0:
                detail_url = self.page_domain % item
                page_list.append(scrapy.Request(self.page_domain % detailurl, callback=self.parse_detail, method='get',
                                                errback=self.handle_error))
        return page_list



    def parse_detail(self,response):
        item = {}
        title = "".join(response.xpath("//strong[1]/text()").re('[^\s]'))
        item['title'] = title
        if response.css(".law_content .STitle")!=None and title!='':
           STitle = "".join(response.css(".law_content .STitle").re('[^\s]')).split("<br>")
           item['anNo']=None
           item['pubish_time'] = None
           item['effect_time'] = None
           item['pubish_org'] = None
           item['level']=None
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
          # self.statuteData.insert_statute((uid,u'',item['effect_time'],item['level'],item['pubish_time'],item['title'],item['anNo'],item['source'],item['pubish_org'],item["content"],0))
           del  item["content"]
           print item



    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)




