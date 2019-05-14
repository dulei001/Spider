#!/usr/bin/python
#-*- coding: utf-8 -*-
import uuid
from dal.service.UserInfoInfoData import UserInfoInfoData
class LawyerWriterPipeline(object):
    def __init__(self):
        self.userInfoInfoData = UserInfoInfoData()

    def process_item(self, item, spider):
        line = dict(item)
        if line.has_key('UILawNumber'):
            if line.has_key('UISex')==False:
               line['UISex']=None
            self.userInfoInfoData.insert_temp_userinfo((line["UIID"],
                                                        line["UIPhone"],
                                                        line["UIName"],
                                                        line["UIEmail"],
                                                        line["UIPic"],
                                                        line["UILawNumber"],
                                                        line["LawOrg"],
                                                        line["ProvinceCode"],
                                                        line["CityCode"],
                                                        line["Address"],
                                                        line["UISignature"],
                                                        line['UISex']
                                                        ))
            if line.has_key('fiil_str'):
                try:
                    for fiid in item['fiil_str']:
                        self.userInfoInfoData.insert_temp_userfield(
                            (str(uuid.uuid1()).replace('-', ''), fiid, line["UIID"]))
                except  Exception as e:
                    print e
        return item

    def close_spider(self, spider):
         pass



