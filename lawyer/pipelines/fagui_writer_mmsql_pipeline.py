#!/usr/bin/python
#-*- coding: utf-8 -*-

from dal.service.StatuteData import StatuteData
class FaGuiWriterPipeline(object):
    def __init__(self):
        self.statuteData = StatuteData()

    def process_item(self, item, spider):
        line = dict(item)
        if line.has_key('title'):
            self.statuteData.insert_statute((item['Id'],
                                             item['time_liness'],
                                             item['effect_time'],
                                             item['level'],
                                             item['pubish_time'],
                                             item['title'],
                                             item['anNo'],
                                             item['source'],
                                             item['pubish_org'],
                                             item["content"],
                                             item['provinceName'],
                                             item['cityName'],
                                             item['provinceCode'],
                                             item['cityCode'],
                                             item['sIndex'],
                                             item['sTypeName'],
                                             0))
            return item

    def close_spider(self, spider):
         pass



