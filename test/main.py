#!/usr/bin/python
#-*- coding: utf-8 -*-

from dal.service.AreaData import  AreaData
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
if __name__ =="__main__":
    areaData =AreaData()
    print areaData.find_area_by_name_return_code((u'北京',))
    pass





