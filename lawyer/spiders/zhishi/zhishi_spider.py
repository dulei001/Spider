#!/usr/bin/python
#-*- coding: utf-8 -*-
import re
import scrapy
import uuid
from  dal.service.LawKnowData import LawKnowData


class ZhiShiSpider(scrapy.Spider):
   #家律网
    name = "zhishi_spider"
    allowed_domains = ["www.jialvwang.com"]
    start_urls = [
        'http://www.jialvwang.com/news'
    ]

    # 初始化打开数据库
    def __init__(self):
        print "spider start..........................."
        super(ZhiShiSpider, self).__init__(self)
        self.LawKnowData = LawKnowData()

    # 关闭数据库
    def close(self):
         print "spider stop..........................."

    def parse(self, response):
        for item in response.css(".nav_rd_z a"):
            menu = item.xpath("text()").extract_first()
            if menu not in (u'法规首页', u'关注公众号'):
                uid=str(uuid.uuid1()).replace('-','')
                # 插入一级菜单
                menudata = self.LawKnowData.query_lawknow_menu_one((menu,))
                if menudata == None:
                    self.LawKnowData.insert_lawknow_menu((uid, menu, None))
                else:
                    uid = menudata[0]
                yield  scrapy.Request(item.xpath("@href").extract_first(),
                                  callback=self.parse_typelist,
                                  method='get',
                                  meta={'parent_id':uid},
                                  errback=self.handle_error)



    def parse_typelist(self,response):
        parent_id = response.meta['parent_id']
        for item in  response.css('.a2 a'):
            uid = str(uuid.uuid1()).replace('-', '')
            name =item.xpath('text()').extract_first()
            page_list_url = item.xpath("@href").extract_first()
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
        has_next = len(response.css('.news_2 ul li'))>0
        request_arrs=[]
        if has_next:
            page= 2 if response.meta.has_key("page")==False else int(response.meta['page'])
            page_url= re.sub('&page=\d+','',response.url)+"&page={0}"
            page_url = str(page_url).format(page)
            request_arrs.extend(self.parse_list_table(response))
            request_arrs.append(scrapy.Request(page_url,
                                     callback=self.parse_list,
                                     method='get',
                                     meta={'parent_id': parent_id,'page':page+1},
                                     errback=self.handle_error))
            return  request_arrs

    def parse_list_table(self,response):
        parent_id = response.meta['parent_id']
        for item in response.css(".news_2 ul li"):
             spider_url = item.xpath("a/@href").extract_first()
             has_url = self.LawKnowData.query_exists_lawknow_by_url((spider_url,))
             if has_url != None:
                print "url is exists!"
                continue
             pub_time =item.xpath("span/text()").extract_first()
             yield scrapy.Request( spider_url,
                                  callback=self.parse_detail,
                                  method='get',
                                  meta={'parent_id': parent_id,'pub_time':pub_time},
                                  errback=self.handle_error)




    def parse_detail(self,response):
        item ={}
        #二级菜单ID
        item['parentId'] = response.meta['parent_id']
        item['pub_time'] = response.meta['pub_time']
        item['title'] = response.xpath('//h1[@id="title"]/text()').extract_first()
        content= ''.join(response.xpath("//div[@id='content']/*").extract()).replace("\r","").replace("\n","").replace("\t","").replace(" ","")
        content = re.sub(r'(<a.*?>.*?</a>)|(<img.*?>)|((class|style|color|href)="[^"]*?")', '', content).replace(u'本文旨在传播更多信息，无任何商业用途，如有侵权请告知删除。','').replace(u'大家还有什么不懂的话可以来家律网进行','').replace(u'家律网','').replace(u"搜集整理。",'').replace('http://www.jialvwang.com','')  # 内容'''
        item['content'] = content
        item['url'] = response.url
        item['title'] = item['title'] if item['title']!=None else ''
        #ID, Title,Content,MenuId,PubDate,BrowCount
        if item['content'] !='' or item['content'] !=None:
            self.LawKnowData.insert_lawkno((str(uuid.uuid1()).replace('-', ''),
                                            item['title'],
                                            item['content'],
                                            item['parentId'],
                                            item['pub_time'],
                                            0,
                                            u'家律网',
                                            response.url
                                            ))
        del item['content']
        return item

    def handle_error(self, result, *args, **kw):
         print "error url is :%s" % result.request.url
         self.logger.error("error url is :%s" % result.request.url)


