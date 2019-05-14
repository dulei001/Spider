#!/usr/bin/python
#-*- coding: utf-8 -*-
import re
import uuid
import scrapy

class npcxjShengSpider(scrapy.Spider):
    # 中国法律法规信息库

    name = "npcxj"
    provinceName = u"新疆"
    provinceCode = '65'
    txtid = '82'
    total = 780

    level = u"地方法规"
    start_urls = ['http://law.npc.gov.cn/FLFG/ksjsCateGroup.action']

    page_list_demon='http://law.npc.gov.cn/FLFG/flfgByID.action?flfgID={0}&zlsxid={1}'


    def parse(self, response):
        page = (self.total+1) /(50-1)
        list_url = "http://law.npc.gov.cn/FLFG/getAllList.action?SFYX=%E6%9C%89%E6%95%88,%E5%B7%B2%E8%A2%AB%E4%BF%AE%E6%AD%A3,%E5%A4%B1%E6%95%88&txtid={0}&pagesize=50&curPage={1}"
        for item in range(1,page):
            yield scrapy.Request(url=list_url.format(self.txtid,item),callback=self.parse_list, errback=self.handle_error)


    def parse_list(self,response):
        for item in response.css('table tr:not(#id) a'):
            url= ''.join(item.css("::attr(href)").re('[^\s+]'))
            if 'javascript:void(0);'!=url and url.find('javascript:pagecss')==-1 and url.find('javascript:toUpDownPage')==-1 :
                if url.find('http')==-1:
                    url=self.page_list_demon.format(str(re.search(r"'(\d+)','','(\d+)'", url).group(1)), str(re.search(r"'(\d+)','','(\d+)'", url).group(2)))
                yield scrapy.Request(url, callback=self.parse_detail, method='get',errback=self.handle_error)


    def parse_detail(self,response):
        item = {}
        title = ''.join(response.css('.bt::text').re('[^\s+]'))
        if title != '':
            item['title'] = title
            item['anNo'] = ''.join(response.xpath('//*[@id="content"]/table/tr[3]/td[2]/text()').re('[^\s+]'))
            item['pubish_time'] = ''.join(response.xpath('//*[@id="content"]/table/tr[4]/td[4]/text()').re('[^\s+]')).replace(u"年","-").replace(u"月","-").replace(u"日","")
            item['effect_time'] = ''.join(response.xpath('//*[@id="content"]/table/tr[4]/td[2]/text()').re('[^\s+]')).replace(u"年","-").replace(u"月","-").replace(u"日","")
            item['pubish_org'] = ''.join(response.xpath('//*[@id="content"]/table/tr[2]/td[2]/text()').re('[^\s+]'))
            item['level'] = self.level
            lev=''.join(response.xpath('//*[@id="content"]/table/tr[5]/td[2]/text()').re('[^\s+]'))
            if lev==u'有效':
                item['time_liness'] = u"现行有效"
            elif lev == u'失效':
                item['time_liness'] = u"已失效"
            elif lev == u'已修正':
                item['time_liness'] = u"已被修正"
            else:
                item['time_liness'] = u"现行有效"
            content = ''.join(response.css('.nr').extract())
            item["content"] = re.sub('((id|class|style|color|href|target|align|title)="[^"]*?")|(<img .*?>)', '',content).replace('\t','').replace('\n','').replace('\r','')   # 内容'''
            #item["content"] = ''
            item['url'] = response.url
            item["provinceName"] = self.provinceName
            item["provinceCode"] = self.provinceCode
            item["cityName"] = None
            item["cityCode"] = None
            item['sIndex'] = None
            item["sTypeName"] = None
            item['source'] = u"中国法律法规信息库"
            # 是否导入正式数据库
            item['export'] = '0'
            item['collection'] = 'fagui'
            item["Id"] = str(uuid.uuid1()).replace('-', '')
            return item

        pass


    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)