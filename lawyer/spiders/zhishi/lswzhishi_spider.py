#!/usr/bin/python
#-*- coding: utf-8 -*-
import re
import scrapy
import uuid
from  dal.service.LawKnowData import LawKnowData

class lswZhiShiSpider(scrapy.Spider):
   #律师屋
    name = "lswzhishi_spider"
    allowed_domains = ["www.lvshiwu.com"]
    start_urls = [
        'https://www.lvshiwu.com'
    ]
    demo='http://www.lvshiwu.cn'
    LawKnowData = LawKnowData()
    # 初始化打开数据库
    def __init__(self):
        print "spider start..........................."
        super(lswZhiShiSpider, self).__init__(self)

    # 关闭数据库
    def close(self):
         print "spider stop..........................."

    def parse(self, response):
        for item in response.xpath("//div[@class='ban']/ul/li[position()>1]/a"):
            menu = item.xpath("text()").extract_first()
            uid = str(uuid.uuid1()).replace('-', '')
            # 插入一级菜单
            menudata = self.LawKnowData.query_lawknow_menu_one((menu,))
            if menudata == None:
                self.LawKnowData.insert_lawknow_menu((uid, menu, None))
            else:
                uid = menudata[0]
            yield scrapy.Request(item.xpath("@href").extract_first(),
                                 callback=self.parse_typelist,
                                 method='get',
                                 meta={'parent_id': uid},
                                 errback=self.handle_error)



    def parse_typelist(self,response):
        parent_id = response.meta['parent_id']
        for item in  response.css('.lanmua a'):
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
        page_count = response.xpath('//select[@name="sldd"]/option/@value').extract()
        if len(page_count)>0:
            page_url= response.url+"{0}"
            for page in page_count:
              yield scrapy.Request(str(page_url).format(page),
                                     callback=self.parse_list_table,
                                     method='get',
                                     meta={'parent_id': parent_id},
                                     errback=self.handle_error)

    def parse_list_table(self,response):
        parent_id = response.meta['parent_id']
        for item in response.css(".nmleftlist dl"):
             pub_time=  ''.join(item.xpath("span[1]/text()").extract()).replace(u"发表时间： ",'')
             spider_url=item.xpath("dt/a/@href").extract_first()
             has_url = self.LawKnowData.query_exists_lawknow_by_url((spider_url,))
             if has_url != None:
                 print "url is exists!"
                 continue
             yield scrapy.Request(spider_url,
                                  callback=self.parse_detail,
                                  method='get',
                                  meta={'parent_id': parent_id,'pub_time':pub_time},
                                  errback=self.handle_error)




    def parse_detail(self,response):
        item ={}
        #if self.LawKnowData.query_exists_lawknow_by_url((response.url,)) == None:
        #二级菜单ID
        item['parentId'] = response.meta['parent_id']
        item['pub_time'] = response.meta['pub_time']
        item['title'] = response.css('.nmcon h1::text').extract_first()
        content= ''.join(response.xpath("//div[@class='content']").extract())
        content = re.sub(r'(<a.*?>.*?</a>)|(<op.*?>.*?</op>)|(<img.*?>)|(<hr.*?>)|((class|style|color|href)="[^"]*?")', '', content).replace("\r","").replace("\n","").replace("\t","").replace(" ","")  # 内容'''
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
                                            u'律师屋',
                                            response.url
                                            ))
        del item['content']
        return item

    def handle_error(self, result, *args, **kw):
         print "error url is :%s" % result.request.url
         self.logger.error("error url is :%s" % result.request.url)


