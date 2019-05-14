#!/usr/bin/python
#-*- coding: utf-8 -*-
import re
import scrapy
import uuid
from  dal.service.LawKnowData import LawKnowData

class dlsZhiShiSpider(scrapy.Spider):
   #大律师
    name = "dlszhishi_spider"
    allowed_domains = ["www.maxlaw.cn"]
    start_urls = [
        'http://www.maxlaw.cn/zhishi'
    ]
    demo='http://www.maxlaw.cn'
    LawKnowData = LawKnowData()
    # 初始化打开数据库
    def __init__(self):
        print "spider start..........................."
        super(dlsZhiShiSpider, self).__init__(self)

    # 关闭数据库
    def close(self):
         print "spider stop..........................."

    def parse(self, response):
        for item in response.css(".nav-bar a"):
                menu = item.xpath("text()").extract_first()
                uid=str(uuid.uuid1()).replace('-','')
                #插入一级菜单
                menudata = self.LawKnowData.query_lawknow_menu_one((menu,))
                if menudata==None:
                   self.LawKnowData.insert_lawknow_menu((uid, menu, None))
                else:
                   uid = menudata[0]
                yield  scrapy.Request(self.demo+item.xpath("@href").extract_first(),
                                  callback=self.parse_typelist,
                                  method='get',
                                  meta={'parent_id':uid},
                                  errback=self.handle_error)



    def parse_typelist(self,response):
        parent_id = response.meta['parent_id']
        for item in  response.css('.bar-box a'):
            uid = str(uuid.uuid1()).replace('-', '')
            name =item.xpath('text()').extract_first()
            page_list_url = self.demo+item.xpath("@href").extract_first()
            menudata = self.LawKnowData.query_lawknow_sub_menu_one((name,))
            if menudata == None:
                self.LawKnowData.insert_lawknow_menu((uid, name, parent_id))
            else:
                uid = menudata[0]
            yield scrapy.Request(page_list_url,
                                 callback=self.parse_list,
                                 method='get',
                                 meta={'parent_id': uid},
                                 errback=self.handle_error)
    def parse_list(self,response):
        parent_id = response.meta['parent_id']
        page_count = response.xpath('//div[@class="almbfy clearfix"]/span/a[3]/text()').extract()
        if len(page_count)>0:
            page_url= response.url+"-p{0}"
            for page in range(1,int(page_count[0])):
              yield scrapy.Request(str(page_url).format(page),
                                     callback=self.parse_list_table,
                                     method='get',
                                     meta={'parent_id': parent_id},
                                     errback=self.handle_error)

    def parse_list_table(self,response):
        parent_id = response.meta['parent_id']
        for item in response.css(".rhyju a"):
             spider_url=self.demo+item.xpath("@href").extract_first()
             has_url = self.LawKnowData.query_exists_lawknow_by_url((spider_url,))
             if has_url != None:
                print "url is exists!"
                continue
             yield scrapy.Request(spider_url,
                                  callback=self.parse_detail,
                                  method='get',
                                  meta={'parent_id': parent_id},
                                  errback=self.handle_error)




    def parse_detail(self,response):
            item ={}
            #二级菜单ID
            item['parentId'] = response.meta['parent_id']
            item['pub_time'] = ''.join(
                response.xpath('//div[@class="other-left-desc"]/span[2]/text()').extract()).replace(u'时间：', '')
            item['title'] = response.css('.other-left-top h1::text').extract_first()
            content = ''.join(response.xpath("//div[@class='other-left-article']").extract())
            content = re.sub(
                r'(<a.*?>.*?</a>)|(<op.*?>.*?</op>)|(<img.*?>)|(<hr.*?>)|((class|style|color|href)="[^"]*?")', '',
                content).replace("\r", "").replace("\n", "").replace("\t", "").replace('&lt;/script&gt;', '').replace(
                " ", "")  # 内容'''
            item['content'] = content
            item['url'] = response.url
            item['title'] = item['title'] if item['title'] != None else ''
            # ID, Title,Content,MenuId,PubDate,BrowCount
            if item['content'] != '' or item['content'] != None:
                self.LawKnowData.insert_lawkno((str(uuid.uuid1()).replace('-', ''),
                                                item['title'],
                                                item['content'],
                                                item['parentId'],
                                                item['pub_time'],
                                                0,
                                                u'大律师网',
                                                response.url
                                                ))
            del item['content']
            return item

    def handle_error(self, result, *args, **kw):
         print "error url is :%s" % result.request.url
         self.logger.error("error url is :%s" % result.request.url)


