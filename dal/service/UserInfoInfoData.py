#!/usr/bin/python
# -*- coding: utf-8 -*-
from dal.com.MSSQLBasic import MSSQLBasic
'''
author:dl
date:2018/9/3
desc:操作律师临时表
'''
class UserInfoInfoData(MSSQLBasic):
    # 添加用户临时表
    def insert_temp_userinfo(self, pamar):
        sql = "INSERT INTO [tb_UserInfoTemp] ([UIID],[UIPhone] ,[UIRegTime] ,[UIRegType] ,[UIState],[UIName] ,[UIEmail] ,[UIPic],[UILawNumber],[LawOrg],[ProvinceCode],[CityCode],[Address],[UISignature],[UISex]) "
        sql += " VALUES(%s,%s,getdate(),0, 3,%s,%s,%s,%s,%s,%s,%s,%s,%s,%d)"
        self.con.exec_no_query(sql, pamar)

    def insert_temp_userfield(self, pamar):
        sql = "INSERT INTO [tb_UserFieldTemp] (UFID,FIID ,UserID) "
        sql += " VALUES(%s,%s,%s)"
        self.con.exec_no_query(sql, pamar)

    def find_lawyer_by_lawlumber(self, pamar):
        sql = 'select UIID from  tb_UserInfoTemp  where UILawNumber = %s'
        return self.con.exec_query_one(sql, pamar)