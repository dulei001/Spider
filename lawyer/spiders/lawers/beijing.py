#!/usr/bin/python
#-*- coding: utf-8 -*-
import scrapy

from devops import scrapyd_deploy
from devops import scrapyd_scheduling
from lawyer import http_util
from lawyer.items.LawyerInfo_item import LawyerInfoItem


class BeijingSpider(scrapy.Spider):
    name = "beijing_lawyer_spider"
    start_urls = ["http://www.bjsf.gov.cn/publish/portal0/tab143/"]

    def parse(self, response):
        list_url=response.xpath('//iframe[@id="main"]/@src').extract_first()
        for page in range(1,3489):
            content_type, body = http_util.multpart_encode({
                "__EVENTTARGET": "ess$ctr706$LawyerSearchList$lbtnGoto",
                "__EVENTARGUMENT": "",
                "__VIEWSTATE": "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",
                "__VIEWSTATEENCRYPTED": "",
                "ScrollTop": "",
                "__essVariable": '{"__scdoff":"1"}',
                "ess$ctr706$LawyerSearchList$txtName": "",
                "ess$ctr706$LawyerSearchList$txtCodeNum": "",
                "ess$ctr706$LawyerSearchList$txtOfficeName": "",
                "ess$ctr706$LawyerSearchList$ddlType": "-1",
                "ess$ctr706$LawyerSearchList$txtPageNum": str(page)})

            yield scrapy.Request(url=list_url,
                           method="POST",
                           headers={"Content-Type": content_type},
                           body=body,
                           callback=self.parse_lawyer_list,
                           errback=self.handle_error)

    def parse_lawyer_list(self,response):
        send_requests=[]
        iframe_detail_urls=response.xpath('//table[@class="datagrid-main"]/tr/td/a/@href').extract()
        for iframe_detail_url in iframe_detail_urls:
            send_requests.append(scrapy.Request(url=iframe_detail_url,
                                                callback=self.parse_lawyer_iframe_detail,
                                                errback=self.handle_error))
        return send_requests

    def parse_lawyer_iframe_detail(self, response):
        detail_url = response.xpath('//iframe[@id="main"]/@src').extract_first()
        detail_id=response.url.split("?itemid=")[1]
        return scrapy.Request(url=detail_url+"?itemid="+detail_id,
                              callback=self.parse_lawyer_item,
                              errback=self.handle_error)

    def parse_lawyer_item(self, response):
        item=LawyerInfoItem()
        item["name"]=response.xpath('//span[@id="ess_ctr742_LawyerView_lblName"]/text()').extract_first()
        item["sex"] = 0 if response.xpath('//span[@id="ess_ctr742_LawyerView_lblSex"]/text()').extract_first()==u"男" else 1
        item["nation"]=response.xpath('//span[@id="ess_ctr742_LawyerView_lblFolk"]/text()').extract_first()
        item["education"] = response.xpath('//span[@id="ess_ctr742_LawyerView_lblEdu"]/text()').extract_first()
        item["political_status"]=response.xpath('//span[@id="ess_ctr742_LawyerView_lblParty"]/text()').extract_first()
        item["headurl"]= ''.join(http_util.downloadImage(["http://app.bjsf.gov.cn"+response.xpath('//img[@id="ess_ctr742_LawyerView_Image1"]/@src').extract_first()],'lawyer_pics/beijing'))
        item["lawnumber"] = response.xpath('//span[@id="ess_ctr742_LawyerView_lblCertificate_Code"]/text()').extract_first()
        item["professional_status"] = 0 if response.xpath('//span[@id="ess_ctr742_LawyerView_lblStatus"]/text()').extract_first()==u"执业" else 1
        item["personnel_type"] = response.xpath('//span[@id="ess_ctr742_LawyerView_lblPerson_Type"]/text()').extract_first()
        start_time = response.xpath('//span[@id="ess_ctr742_LawyerView_lblFirst_Date"]/text()').extract_first()
        if start_time!=None:
            item["start_time"] = start_time.replace("/","-")
        get_time=response.xpath('//span[@id="ess_ctr742_LawyerView_lblCompetency_Date"]/text()').extract_first()
        if get_time!=None:
            item["get_time"] = get_time.replace("/","-")
        item["cert_type"] = response.xpath('//span[@id="ess_ctr742_LawyerView_lblCompetency_Type"]/text()').extract_first()
        item["profession"] = ''
        item["ispartnership"] = 0 if response.xpath('//span[@id="ess_ctr742_LawyerView_lblIsCopartner"]/text()').extract_first()==u"否" else 1
        item["firm"] =response.xpath('//span[@id="ess_ctr742_LawyerView_lblLo_Name"]/text()').extract_first()
        item["province"] =u"北京"
        item['collection'] = 'lawyers'
        item["url"]=response.url


        return item

    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)

if __name__ == '__main__':
    # 部署整个工程
    scrapyd_deploy.deploy()
    # 运行spider
    scrapyd_scheduling.schedule(project="lawyer", spider="beijing_lawyer_spider")
    # 取消运行spder 执行三次
    # scrapyd_cencel.cancel(project="lawyer",job="fbbfb9ecf42a11e699010242c0a80004")