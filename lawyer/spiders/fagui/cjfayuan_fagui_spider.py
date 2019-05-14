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
class cjfayuan_fagui_spider(scrapy.Spider):
    """财经法规"""

    name = "cjfyfagui"
    statuteData = StatuteData()
    allowed_domains=["www.chinaacc.com"]

    start_urls = [
       # 'http://www.chinacourt.org/law/more/law_type_id/MzAwNEAFAA%3D%3D/page/1.shtml', #国家法规库
        #'https://www.chinacourt.org/law/more/law_type_id/MzAwM0AFAA%3D%3D.shtml', #司法解释
        'http://www.chinaacc.com/fagui/search.shtm',#地方法规
        #'https://www.chinacourt.org/law/more/law_type_id/MzAwMUAFAA%3D%3D/page/1.shtml'#政策参考
        ]
    page_domain = "http://www.chinaacc.com%s"

    def parse(self, response):
       pageurl='http://www.chinaacc.com/dffg/page{0}.shtm'
       for item in range(1,4120):
            yield  scrapy.Request(pageurl.format(str(item)),callback=self.parse_list,method='get',errback=self.handle_error)


    def parse_list(self,response):
        for item in response.xpath('//div[@class="lqnr clearfix"]/dl/dd'):
            detailurl = item.css('a::attr(href)').extract_first()
            detail_url = self.page_domain % detailurl
            yield   scrapy.Request(detail_url, callback=self.parse_detail, method='get',
                                                errback=self.handle_error)


    def parse_detail(self,response):
        item = {}
        item['title'] = response.xpath("//div[@class='top clearfix']/h1/text()").extract_first()
        # 发文字号
        item['anNo'] = ''.join(response.xpath("//div[@class='top clearfix']").css(".c::text").extract())
        # 颁布日期
        item['pubish_time'] = ''.join(response.xpath("//div[@class='top clearfix']").css(".b::text").re('[^\s]')).replace(u'颁布时间：','').replace('\n','').replace('\r','').replace('\t','').replace(' ','')

        # 生效日期
        item['effect_time'] = ''.join(response.xpath("//div[@class='top clearfix']").css(".b::text").re('[^\s]')).replace(u'颁布时间：','').replace('\n','').replace('\r','').replace('\t','').replace(' ','')

        # 颁布机构
        item['pubish_org'] = ''.join(response.xpath("//div[@class='top clearfix']").css(".b span::text").re('[^\s]')).replace(u'发文单位：','').replace('\n','').replace('\r','').replace('\t','').replace(' ','')

        # 效力级别
        item['level'] =u'地方法规'
        # 时效性
        item['time_liness'] = ""
        content = ''.join(response.xpath('//div[@class="cen clearfix"]').extract())
        item["content"] = re.sub('(class|style|color|href|target|align)="[^"]*?"', '', content).replace(u'【','').replace(u'我要纠错','').replace(u'】 责任编辑：','').replace(u'大白兔','').replace(u'小海鸥','').replace('qzz','')  # 内容'''
        item['url'] = response.url
        item['source'] = u"中华会计网校"
        # 是否导入正式数据库
        item['export'] = '0'
        item['collection'] = 'fagui'
        uid = str(uuid.uuid1()).replace('-', '')
        # Id,Time_liness,Effect_time,Level,Pubish_time,Title,AnNo,Source,Pubish_org,Content,IsBuild
        self.statuteData.insert_statute((uid, u'', item['effect_time'], item['level'], item['pubish_time'],
                                         item['title'], item['anNo'], item['source'], item['pubish_org'],
                                         item["content"], 0))
        del item["content"]
        print item




    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)




