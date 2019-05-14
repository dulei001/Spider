#!/usr/bin/python
#-*- coding: utf-8 -*-
import re
import uuid
import json
import scrapy

class NMGRDSpider(scrapy.Spider):
    # 内蒙古人大

    name = "nmgrd"
    provinceName = u"内蒙古"
    provinceCode='15'
    level = u"地方法规"
    pubish_time='2019-04-26'

    allowed_domains=["www.nmgrd.gov.cn"]

    start_urls = [ 'http://www.nmgrd.gov.cn/']

    fgparamlist = [
        {'type': u'自制区法规', 'page': '7', 'url':'/lfgz/fg/xxqfg/','cityCode':None,'cityName':None},
        {'type': u'呼和浩特市法规', 'page': '3', 'url': '/lfgz/fg/hhhtfg/', 'cityCode': '1506', 'cityName': u'呼和浩特市'},
        {'type': u'包头市法规', 'page': '3', 'url': '/lfgz/fg/btfg/', 'cityCode': '1503', 'cityName': u'包头市'},
        {'type': u'通辽市法规', 'page': '1', 'url': '/lfgz/fg/tlsfg/', 'cityCode': '1508', 'cityName': u'通辽市'},
        {'type': u'赤峰市法规', 'page': '1', 'url': '/lfgz/fg/dfsfg/', 'cityCode': '1504', 'cityName': u'赤峰市'},
        {'type': u'乌兰察布市法规', 'page': '1', 'url': '/lfgz/fg/wlcbsfg/', 'cityCode': '1510', 'cityName': u'乌兰察布市'},
        {'type': u'巴彦淖尔市法规', 'page': '1', 'url': '/lfgz/fg/bynrsfg/', 'cityCode': None, 'cityName': u'巴彦淖尔市'},
        {'type': u'莫力达瓦达斡尔族自治旗法规', 'page': '1', 'url': '/lfgz/fg/mdl/', 'cityCode': '1507', 'cityName': u'呼伦贝尔市'},
        {'type': u'鄂伦春自治旗法规', 'page': '1', 'url': '/lfgz/fg/elc/', 'cityCode': '1507', 'cityName': u'呼伦贝尔市'},
        {'type': u'鄂温克族自治旗法规', 'page': '1', 'url': '/lfgz/fg/ewk/', 'cityCode': '1507', 'cityName': u'呼伦贝尔市'},
        {'type': u'废止的地方性法规决定', 'page': '2', 'url': '/lfgz/fg/xxqfg_1/', 'cityCode': None, 'cityName':None}
    ]

    page_domain = "http://www.nmgrd.gov.cn%s"

    def parse(self, response):
        send_requests = []

        for item in self.fgparamlist:
            page = int(item['page'])
            url = item['url']
            for index in range(1, page + 1):
                if index == 1:
                    send_requests.append(scrapy.Request(self.page_domain % url, callback=self.parse_list, method='get',
                                                        errback=self.handle_error, meta={'type': item['type'],'levelurl': item['url'],'cityCode':  item['cityCode'],'cityName': item['cityName']}))
                else:
                    p = index - 1
                    newurl = ''.join((url, 'index_%d.html' % p))
                    send_requests.append(
                        scrapy.Request(self.page_domain % newurl, callback=self.parse_list, method='get',
                                       errback=self.handle_error, meta={'type': item['type'],'levelurl': item['url'],'cityCode':  item['cityCode'],'cityName': item['cityName']}))

        return send_requests


    def parse_list(self, response):
        levelurl=response.meta['levelurl']

        for item in response.css(".hhh14"):
            detail_url=''
            content=''.join(item.css("::text").extract())
            links =re.findall(r"href='(.+?)'", content)[0]
            if '../../../' in links:
                links=links.replace('../../../','/')
                detail_url = links
            else:
                links = links.replace('./', '')
                detail_url =''.join((levelurl,links))
            #print self.page_domain % detail_url
            yield scrapy.Request(self.page_domain % detail_url, callback=self.parse_detail, method='get',
                                errback=self.handle_error,meta={'type': response.meta['type'],'cityCode': response.meta['cityCode'],'cityName': response.meta['cityName']})
        pass


    def parse_detail(self,response):
        item = {}
        type=response.meta['type']
        cityCode = response.meta['cityCode']
        cityName = response.meta['cityName']
        title = ''.join(response.css('.content_title::text').re('[^\s+]'))
        if title != '':
            item['title'] = title
            item['anNo'] = None
            item['pubish_time'] = ''.join(response.css('.content_time::text').re('[^\s+]')).replace(u"信息来源：","").replace(u"内蒙古人大网","").replace(u"发布时间：","")
            item['effect_time'] = None
            item['pubish_org'] = u'内蒙古人大'
            item['level'] = self.level
            item['time_liness'] = u"现行有效"
            content = ''.join(response.css('.content_text').extract())
            item["content"] = re.sub('((class|style|color|href|target|align|title)="[^"]*?")|(<img .*?>)', '',content)  # 内容'''
            #item["content"] = ''
            item['url'] = response.url
            item["provinceName"] = self.provinceName
            item["provinceCode"] = self.provinceCode
            item["cityCode"] =None if cityCode==''else cityCode
            item["cityName"] =None if cityName=='' else cityName
            item['sIndex'] =None
            item["sTypeName"] =u'其他'
            item['source'] = u"内蒙古人大"
            # 是否导入正式数据库
            item['export'] = '0'
            item['collection'] = 'fagui'
            item["Id"] = str(uuid.uuid1()).replace('-', '')
            return item


    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)