#!/usr/bin/python
#-*- coding: utf-8 -*-
import re
import scrapy
import uuid
from  dal.service.ChargeData import ChargeData


class ZuiMingSpider(scrapy.Spider):
   #找法网
    name = "zuiming_spider"
    allowed_domains = ["china.findlaw.cn"]
    start_urls = [
        'http://china.findlaw.cn/zuiming/'
    ]
    #构成要素url
    zuiming_menu = ['gainian','tezheng','rending','chufa','fatiao','jieshi']
    #详细页面url
    gainianurl = 'http://china.findlaw.cn/zuiming/{0}/{1}.html'

    # 初始化打开数据库
    def __init__(self):
        print "spider start..........................."
        super(ZuiMingSpider, self).__init__(self)
        self.ChargeData = ChargeData()

    # 关闭数据库
    def close(self):
         print "spider stop..........................."

    def parse(self, response):
        send_requests = []
        for item in   response.xpath("//ul[@class='sidenav']/li"):
             sitem = {};
             typeid = ''.join(item.xpath('a/@typeid').re('[^\s]'))
             sitem["name"]= ''.join(item.xpath('a/text()').re('[^\s]'))
             sitem['uiid']= str(uuid.uuid1()).replace('-','')
             send_requests.append(sitem)
             typeurl = 'http://china.findlaw.cn/zuiming/index.php?m=index&requestmode=async&a=getkw&typeid='+typeid
             send_requests.append(scrapy.Request(typeurl,
                                  callback=self.parse_typelist,
                                  method='get',
                                  meta={'refid':sitem['uiid']},
                                  errback=self.handle_error))
             #写入数据库
             self.ChargeData.insert_charge_menu((sitem['uiid'], sitem['name'], None))
        return send_requests

    def parse_typelist(self,response):
        refid = response.meta['refid']
        send_requests = []
        for item in  response.xpath('//dd/a'):
            sitem ={ }
            sitem['uiid'] = str(uuid.uuid1()).replace('-', '')
            sitem['refid']= refid
            sitem['name'] =item.xpath('text()').extract_first()
            page_number = re.search(r'(\d+_\d+)',item.xpath('@href').extract_first()).group()
            send_requests.append(sitem)
            #写入数据库
            self.ChargeData.insert_charge_menu((sitem['uiid'], sitem["name"], refid))
            for subitem in self.zuiming_menu:
                bodyScrapyUrl = self.gainianurl.format(page_number, subitem)
                idx = self.zuiming_menu.index(subitem)
                send_requests.append(scrapy.Request(bodyScrapyUrl,
                                                    callback=self.parse_detail,
                                                    method='get',
                                                    meta={'idx': idx ,'refid':sitem['uiid']},
                                                    errback=self.handle_error))
        return send_requests

    def parse_detail(self,response):
        item ={}
        #二级菜单ID
        item['parentId'] = response.meta['refid']
        #二级菜单下标
        item['flag'] = response.meta['idx']
        item['title'] = response.css('.textart h1::text').extract_first()
        content= ''.join(response.xpath("//div[@class='wztext']/*").extract()).replace("\r","").replace("\n","").replace("\t","").replace(" ","")
        content = re.sub(r'<strong>.*?<a.*?title="(.*?)".*?>.*?</a>.*?</strong>', '', content).replace('推荐：','')  # 内容'''
        item['content'] = content
        item['url'] = response.url
        item['title'] = item['title'] if item['title']!=None else ''
        self.ChargeData.insert_charge((str(uuid.uuid1()).replace('-', ''),item['title'],item['content'],item['parentId'], int(item['flag']) ))
        return item

    def handle_error(self, result, *args, **kw):
         print "error url is :%s" % result.request.url
         self.logger.error("error url is :%s" % result.request.url)


