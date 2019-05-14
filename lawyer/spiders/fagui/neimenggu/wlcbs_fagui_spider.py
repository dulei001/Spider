#!/usr/bin/python
#-*- coding: utf-8 -*-
import re
import uuid
import scrapy
class wlcbsSpider(scrapy.Spider):
    """乌兰察布市"""
    name = "wlcbs"
    provinceName=u"内蒙古"
    cityName=u"乌兰察布市"
    provinceCode="15"
    cityCode = "1510"
    level=u"地方法规"

    start_urls = [
        'http://www.wulanchabu.gov.cn',
        ]
    page_domain = "http://www.wulanchabu.gov.cn%s"
    fagui_statr_arr=[
        {"name":u"通知", "url":"http://www.wulanchabu.gov.cn/active/fpage_1.jsp?psize=30&showpagenum=true&fid=10338&pos={0}","page":7},
        {"name": u"公告",    "url": "http://www.wulanchabu.gov.cn/active/fpage_1.jsp?psize=30&showpagenum=true&fid=10338&pos={0}",  "page": 11},
        {"name": u"其他", "url": "http://www.wulanchabu.gov.cn/active/fpage_11.jsp?psize=30&showpagenum=true&fid=10512&pos={0}", "page": 8},
    ]

    def parse(self, response):
        for item in self.fagui_statr_arr:
             for pages in range(1,int(item["page"]),1):
                  yield  scrapy.Request(str(item["url"]).format(str(pages)), callback=self.parse_page_list, method='get', dont_filter=True,
                                                errback=self.handle_error,meta={'stype':item["name"]})

    def parse_page_list(self,response):
        for item in response.css("td a"):
            detailbaseurl=  self.page_domain % ''.join(item.css("::attr(href)").extract())
            yield scrapy.Request(detailbaseurl, callback=self.parse_detail, method='get',
                                 errback=self.handle_error, meta={'stype': response.meta["stype"]})

    def parse_detail(self,response):
        item = {}
        title = ''.join(response.css('#title::text').re('[^\s+]'))
        item['pubish_org'] = u"乌兰察布市人民政府"
        item['source'] = u"乌兰察布市人民政府"
        item['time_liness'] = u"现行有效"
        item["sTypeName"] = response.meta["stype"]
        # 是否导入正式数据库
        item['export'] = '0'
        item['collection'] = 'fagui'
        item["Id"] = str(uuid.uuid1()).replace('-', '')
        item['url'] = response.url
        item["provinceName"] = self.provinceName
        item["cityName"] = self.cityName
        item["provinceCode"] = self.provinceCode
        item["cityCode"] = self.cityCode
        item['effect_time'] = None
        item['sIndex'] = None
        if  title!='':
           item['title'] = title
           item['anNo']=None
           item['pubish_time'] =re.search(r"(\d{4}-\d{1,2}-\d{1,2})", ''.join(response.css("#otherinfo::text").extract())).group(0)
           item['level']= self.level
           content =  ''.join(response.css('#content').extract())
           item["content"] =re.sub('((id|class|style|color|href|target|align|title)="[^"]*?")|(<img .*?>)|(<style .*?>.*?<\/style>)', '', content)  # 内容'''
        else:
            item['pubish_org'] = u"乌兰察布市人民政府"
            thtml=response.css('#title table tr:nth-child(4) td')
            item['title'] = ''.join(thtml.xpath('div/div[1]/text()').re('[^\s+]'))
            item['anNo'] = ''.join(response.css('#title table tr:nth-child(2) td::text').re('[^\s+]'))
            item['pubish_time'] =  ''.join(thtml.xpath('div/div[3]/div[2]/text()').re('[^\s+]')).replace(u'印发','').replace(u"年","-").replace(u"月","-").replace(u"日","").replace(u' ','')
            item['level'] = self.level
            content = ''.join(response.css('#content1').extract())
            item["content"] = re.sub('((id|class|style|color|href|target|align|title)="[^"]*?")|(<img .*?>)|(<\s*style[^>]*>[^<]*<\s*/\s*style\s*>)', '',   content)\
                .replace('<!--/ewebeditor:page-->','').replace('<!--ewebeditor:page -->','').replace('!--EndFragment-->','').replace('\t','').replace('\n','')  # 内容'''
            return  item

    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)


