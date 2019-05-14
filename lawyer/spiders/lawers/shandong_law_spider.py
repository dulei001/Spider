#!/usr/bin/python
#-*- coding: utf-8 -*-
import json
import uuid

import re
import scrapy

from dal.service.AreaData import AreaData
from dal.service.UserInfoInfoData import UserInfoInfoData
from lawyer import http_util
from   lawyer.spiders.lawers.field_info_dic import field_info_dic
#山东律师抓取
class ShanDongLawyerSpider(scrapy.Spider):
    name = "shandong_law_spider"
    start_urls = ["http://www.sd12348.gov.cn/channels/ch00630/"]
    areaData = AreaData()
    userInfoInfoData= UserInfoInfoData()
    pagesize=20
    provincode='37'
    baseurl = "http://www.sd12348.gov.cn/sftIDC/select/search.do"
    def parse(self, response):
        isflag=0
        for item in  response.css("#cityDiv ul li a::attr(href)").extract():
            if isflag==0:
                isflag=1
                continue
            prostr = item.split(u',')
            citycode =prostr[0].replace(u'javascript:changeCitya(','').replace(u"'",'')
            cityname = prostr[1].replace(u"'",'').replace(u");",'')
            yield scrapy.FormRequest(url=self.baseurl,
                                     method="POST",
                                     headers={'X-Requested-With': 'XMLHttpRequest'},
                                     dont_filter=True,
                                     callback=self.parseAjaxPageList,
                                     errback=self.handle_error,
                                     meta={'pageSize':str(self.pagesize),'areacode':citycode,'cityname':cityname,'type':'lawyer','flag':'0','status':'0'},
                                     formdata={ "page":'1','pageSize':str(self.pagesize),'areacode':citycode,'type':'lawyer','flag':'0','status':'0'}
                                     )

    def parseAjaxPageList(self,response):
        data = json.loads(response.body_as_unicode())
        pagecount = (int(data['totalCount'])-1)/(self.pagesize+1)
        for page  in range(1,pagecount):
            response.meta['page']=str(page)
            yield scrapy.FormRequest(url=self.baseurl,
                                     method="POST",
                                     headers={'X-Requested-With': 'XMLHttpRequest'},
                                     dont_filter=True,
                                     callback=self.parseAjaxList,
                                     errback=self.handle_error,
                                     meta=response.meta,
                                     formdata={"page": str(page), 'pageSize':str(self.pagesize), 'areacode': response.meta['areacode'],'type': 'lawyer', 'flag': '0', 'status': '0'})



    def parseAjaxList(self,response):
        data = json.loads(response.body_as_unicode())
        detail_url='http://sd.12348.gov.cn/sftIDC/lawworkmanage/findPersonnelListByid.do?type=lawyer&id={0}'
        for i in data['list']:
            yield scrapy.FormRequest(url=detail_url.format(i['id']),
                                     method="POST",
                                     headers={'X-Requested-With': 'XMLHttpRequest'},
                                     dont_filter=True,
                                     callback=self.parse_detail,
                                     errback=self.handle_error,
                                     meta={'cityname':response.meta['cityname']},
                                     )

    #详情页面
    def parse_detail(self, response):
        item = {}
        #  #[UIID],[UIPhone] ,[UIName] ,[UIEmail] ,[UIPic],[UILawNumber],[LawOrg],[ProvinceCode],[CityCode],[Address],[UISignature]
        data = json.loads(response.body_as_unicode())
        item["UIID"] = str(uuid.uuid1()).replace('-', '')
        uiphone = data['telnum']
        match_count = len(re.findall(r'[1][3,4,5,6,7,8][0-9]{9}', uiphone))
        item['UILawNumber'] = data['licenseno']
        if item["UILawNumber"] != None and len(item["UILawNumber"]) == 17 and self.userInfoInfoData.find_lawyer_by_lawlumber((item["UILawNumber"],)) == None :
            item["UIPhone"] = None if match_count == 0 else uiphone
            item['UIName'] = data['name']
            item["ProvinceCode"] = self.provincode
            item['LawOrg'] =  data['lawfirmname']
            item['UIEmail'] =None
            item["UISignature"]=data['lawyerinfo']
            item['fiil_str'] = field_info_dic.find_field_by_name(data['zhuangchang'])
            item["Address"] = data['lawfirmaddress']
            item["CityCode"] = ''.join(self.areaData.find_area_by_name_return_code((response.meta['cityname'])))
            # 头像路径
            dirname=self.name
            item["UIPic"] = ''.join(http_util.downloadImage(["http://sd.12348.gov.cn" + data['logourl']], '/AppFile/'+ dirname+"/"+ item["UIID"] + '/head'))
            item['url'] = response.url
            return item



    def handle_error(self, result, *args, **kw):
        print "error url is :%s" % result.request.url
        self.logger.error("error url is :%s" % result.request.url)