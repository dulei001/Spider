#!/usr/bin/python
#-*- coding: utf-8 -*-
import uuid

import re
import scrapy

#法律快车网站爬虫
from dal.service.StatuteData import StatuteData


class LawtimeSpider(scrapy.spiders.Spider):
    name = "lawtime"
    start_urls = [
        "http://law.lawtime.cn/gjfg_2_100.html",
        "http://law.lawtime.cn/gjfg_3_101.html",
        "http://law.lawtime.cn/gjfg_4_102.html",
        "http://law.lawtime.cn/gjfg_5_117.html",
        "http://law.lawtime.cn/sfjs.html",
        "http://law.lawtime.cn/dffg_2_107.html",
        "http://law.lawtime.cn/dffg_3_114.html",
        "http://law.lawtime.cn/dffg_4_116.html",
        "http://law.lawtime.cn/dffg_5_115.html",
        "http://law.lawtime.cn/gjty.html",
        "http://law.lawtime.cn/hygf.html",
        "http://law.lawtime.cn/lfca.html",
        "http://law.lawtime.cn/lifadongtai.html"
    ]
    statuteData = StatuteData()
    #爬虫入口
    def parse(self, response):
        return self.parse_article_count(response)

    # 解析文章数量
    def parse_article_count(self,response):
        page_count=response.xpath('//div[@class="paging"]/a[@class="dot"]/following-sibling::*[1]/text()').extract_first()
        if page_count is None :
            return

        for index in range(1,int(page_count)+1):
            extension_index= response.url.index(".html")
            url=response.url[0:extension_index]+"_"+str(index)+".html"
            yield scrapy.Request(url,callback=self.parse_article_list)

    #获取指定页面的列表
    def parse_article_list(self,response):
        spans=response.xpath('//ul[@class="kc_complex_ul"]/li/span')
        for span in spans:
            article_url=span.xpath("a/@href").extract_first()
            if article_url is not None:
                pass
                yield scrapy.Request("http:"+article_url,callback=self.parse_article)

    #解析文章内容
    def parse_article(self,response):
        item={}
        item["url"]=response.url
        top = response.xpath('//div[@class="a_cont_top"]')
        item['title'] = top.xpath('h1/text()').extract()[0]
        organization=top.xpath('p/span[contains(text(),"颁布单位")]/following-sibling::span[1]/text()'.decode("utf-8")).extract()
        publish_time= top.xpath('p/span[contains(text(),"颁布时间")]/following-sibling::span[1]/text()'.decode("utf-8")).extract()
        release_time= top.xpath('p/span[contains(text(),"实施日期")]/following-sibling::span[1]/text()'.decode("utf-8")).extract()
        level= top.xpath('p/span[contains(text(),"效力级别")]/following-sibling::span[1]/text()'.decode("utf-8")).extract()
        effect= top.xpath('p/span[contains(text(),"时效性")]/following-sibling::span[1]/text()'.decode("utf-8")).extract()
        anNo = top.xpath('p/span[contains(text(),"发文字号")]/following-sibling::span[1]/text()'.decode("utf-8")).extract()
        item['anNo'] = ''
        item['pubish_time'] = ''
        item['effect_time'] = ''
        item['pubish_org'] = ''
        item['level'] = ''
        item['time_liness'] = u'已失效'
        if(len(organization)!=0):
            item['pubish_org'] = organization[0].replace("\r\n","").split(u" ")[0]
        if (len(publish_time) != 0):
            item['pubish_time'] = publish_time[0]
        if (len(release_time) != 0):
            item['effect_time'] = release_time[0]
        if (len(level) != 0):
            item['level'] = level[0].replace("\r\n","")
        if (len(effect) != 0):
            df=effect[0].replace(" ", "").replace("\n", "")
            if df==u'有效':
              item['time_liness'] = u'现行有效'
            else:
              item['time_liness'] = u'已失效'
        if (len(anNo) != 0):
             item['anNo'] = anNo[0].replace("\r\n", "").replace('-','')
            # 是否导入正式数据库
        item['export'] = '0'
        item['source'] = u"法律快车"
        content="".join(response.xpath('//div[@class="a_cont_main"]').extract()).replace('\r\n', '')
        content=re.sub('(class|style|color|href|target|align)="[^"]*?"', '', content)  # 内容'''
        item['content'] = content
        uid = str(uuid.uuid1()).replace('-', '')
        self.statuteData.insert_statute((uid, item['time_liness'], item['effect_time'], item['level'], item['pubish_time'],
                                         item['title'], item['anNo'], item['source'], item['pubish_org'],
                                         item["content"], 0))
        del  item['content']
        print item


