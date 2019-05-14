#!/usr/bin/python
#-*- coding: utf-8 -*-
import uuid

import re
import scrapy

#高顿法规网站爬虫
from dal.service.StatuteData import StatuteData


class GaoDunSpider(scrapy.spiders.Spider):
    name = "gaodun_fagui"
    start_urls = [
        "https://fagui.gaodun.com/",

    ]
    statuteData = StatuteData()
    #爬虫入口
    def parse(self, response):
        return self.parse_article_count(response)

    # 解析文章数量
    def parse_article_count(self,response):
        list_url='https://fagui.gaodun.com/index.php/Search/index/t/1/p/{0}.html'
        for page in range(1,12926):
            yield scrapy.Request(list_url.format(str(page)), callback=self.parse_article_list)


    #获取指定页面的列表
    def parse_article_list(self,response):
        lis=response.xpath('//div[@class="mesgebox"]/ul/li')
        for li in lis:
            article_url= 'https://fagui.gaodun.com'+li.xpath("div[@class='cb randwen randwen_2']/p/a/@href").extract_first()
            src = ''.join(li.css('.yxdbox img::attr(src)').extract())
            level=u'现行有效'
            if src!='':
                level = int(re.match('.*/yx(?P<flag>\d+)[\.]png', src).group('flag'))
                if  level ==2:
                    level=u'已失效'
                if level == 3:
                    level = u'尚未生效'
                if level ==4:
                    level = u'已被修正'
            yield scrapy.Request(article_url,callback=self.parse_article,meta={'level':level})

    #解析文章内容
    def parse_article(self,response):
        item={}
        item["url"]=response.url
        top = response.xpath('//div[@class="topfond tac"]')
        item['title'] = ''.join(top.xpath('h1/text()').extract())
        item['pubish_org'] =''.join(top.xpath('h3/text()').extract())
        item['anNo'] = ''.join(top.xpath('p/text()').extract())
        item['pubish_time']= ''.join(response.xpath(u'//div[@class="towaltext"]/span[contains(text(),"发文时间：")]/text()').extract()).replace(u'发文时间：','').replace(' ','')
        item['effect_time']= ''.join(response.xpath(u'//div[@class="towaltext"]/span[contains(text(),"生效时间：")]/text()').extract()).replace(u'生效时间：','').replace(' ','')
        item['level']= u'行业团体规定'
        item['time_liness'] = response.meta['level']
            # 是否导入正式数据库
        item['export'] = '0'
        item['source'] = u"高顿"
        content="".join(response.xpath('//div[@id="para"]').extract()).replace('\r\n', '')
        content=re.sub('(<a.*?>.*?</a>)|((class|style|color|href|target|align)="[^"]*?")|(<.*?>)|(<[/].*?>)', '', content)  # 内容'''
        item['content'] = content.replace("\r",'').replace("\n",'').replace("\t",'').replace(' ','').replace('附件下载:','')
        uid = str(uuid.uuid1()).replace('-', '')
        if item['content']!='' and item['title']!='':
            self.statuteData.insert_statute((uid, item['time_liness'], item['effect_time'], item['level'], item['pubish_time'],
                                             item['title'], item['anNo'], item['source'], item['pubish_org'],
                                             item["content"], 0))
        del  item['content']
        print item


