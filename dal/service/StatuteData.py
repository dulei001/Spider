#!/usr/bin/python
# -*- coding: utf-8 -*-
from dal.com.MSSQLBasic import MSSQLBasic

'''
author:dl
date:2018/9/17
desc:操作法规库
'''


class StatuteData(MSSQLBasic):
    # 添加法规
    def insert_statute(self, pamar):
        sql = "INSERT INTO tb_Statute (Id,Time_liness,Effect_time,Level,Pubish_time,Title,AnNo,Source,Pubish_org,Content,ProvinceName,CityName,ProvinceCode,CityCode,SIndex,STypeName,IsBuild) "
        sql += " VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%d)"
        self.con.exec_no_query(sql, pamar)
