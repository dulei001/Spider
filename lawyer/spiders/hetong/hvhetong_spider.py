#!/usr/bin/python
#-*- coding: utf-8 -*-
import random
import re
import scrapy
import uuid
from  dal.service.ContractMenuData import ContractMenuData


class HvHeTongSpider(scrapy.Spider):
   #华律合同
    name = "hlhetong"
    allowed_domains = ["www.66law.cn"]
    start_urls = [
        'http://www.66law.cn/contractmodel/all/'
    ]
    host='http://www.66law.cn'
    # 初始化打开数据库
    def __init__(self):
        print "spider start..........................."
        super(HvHeTongSpider, self).__init__(self)
        self.contractMenuData = ContractMenuData()

    # 关闭数据库
    def close(self):
         print "spider stop..........................."

    def parse(self, response):
        for item in response.css(".fl.w220 ul li"):
            fistmenu = item.css(".f14 a::text").extract_first()
            uid = str(uuid.uuid1()).replace('-', '')
            # 插入一级菜单 %s, %s, %s,%d,%d
            self.contractMenuData.insert_contract_menu((uid, fistmenu, None,0,0))
            for subitem in item.css('.ht-mn-more.clearfix span'):
                suburl = self.host+''.join(subitem.css("a::attr(href)").extract())
                submeun = ''.join(subitem.css("a::text").extract())
                seconduid = str(uuid.uuid1()).replace('-', '')
                                                           #ID, Name,PID,Sort,IsDel
                self.contractMenuData.insert_contract_menu((seconduid, submeun, uid, 0, 0))
                yield  scrapy.Request(suburl,
                                  callback=self.parse_list,
                                  method='get',
                                  meta={'parent_id':seconduid},
                                  errback=self.handle_error)


    def parse_list(self,response):
       parent_id = response.meta['parent_id']
       pagestr = ''.join(response.xpath("//div[@class='m-page tc mt40']/a[last()-1]/text()").extract())
       #解析第一页数据
       self.parse_list_table(response)
       if pagestr == '':
           return
       for page in range(2, int(pagestr)):
           yield scrapy.Request(response.url+"page_"+str(page)+".aspx",
                                callback=self.parse_list_table,
                                method='get',
                                meta={'parent_id': parent_id},
                                errback=self.handle_error)

    def parse_list_table(self,response):
        parent_id = response.meta['parent_id']
        for item in response.css(".ht-list  li"):
             detail_url = self.host+item.css(".ht-lt-tit a::attr(href)").extract_first()
             cratetime = ''.join(item.css(".ht-lt-other.mt20 span:nth-child(1)::text").extract())
             yield scrapy.Request(detail_url,
                                  callback=self.parse_detail,
                                  method='get',
                                  meta={'parent_id': parent_id,"cratetime":cratetime},
                                  errback=self.handle_error)




    def parse_detail(self,response):
        item ={}
        #二级菜单ID
        item['parentId'] = response.meta['parent_id']
        item['cratetime'] = None if response.meta['cratetime']=='' else response.meta['cratetime']
        item['title'] = ''.join(response.xpath('//h1[@class="det-title tc"]/text()').extract())
        viewcount =  ''.join(response.xpath('//div[@class="det-infor mt15 tc"]').css(".s-oe::text").extract()).replace("\r", "").replace( "\n", "").replace("\t", "").replace(" ", "")
        item['viewcount']= 0 if viewcount=="" else int(viewcount)
        content= ''.join(response.xpath("//div[@class='det-nr mt20']/*").extract()).replace("\r","").replace("\n","").replace("\t","").replace(" ","")
        content = re.sub(r'(<script.*?>.*?</script>)|(<img.*?>)|((class|style|color|href|target|align|id|title)="[^"]*?")', '', content).replace("\r","").replace("\n","").replace("\t","").replace(" ","")  # 内容'''
        item['content'] = content
        item['url'] = response.url
        item['title'] = item['title'] if item['title']!=None else ''
        #CID, ContractMenuId,Content,Title,Createtime,Url,IsReserve,DownloadCount,ViewCount
        if item['content'] !='' or item['content'] !=None:
            self.contractMenuData.insert_contract((str(uuid.uuid1()).replace('-', ''),
                                           item['parentId'],
                                            item['content'],
                                            item['title'],
                                            item['cratetime'],
                                            item['url'],
                                            0,
                                            random.randint(0, 20000),
                                            viewcount,
                                            ))
        del item['content']
        print item

    def handle_error(self, result, *args, **kw):
         print "error url is :%s" % result.request.url
         self.logger.error("error url is :%s" % result.request.url)


