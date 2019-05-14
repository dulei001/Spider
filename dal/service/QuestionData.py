#!/usr/bin/python
# -*- coding: utf-8 -*-
from dal.com.MSSQLBasic import MSSQLBasic

'''
author:dl
date:2018/9/17
desc:操作问答
'''


class QuestionData(MSSQLBasic):

    # 添加免费问题
    def insert_free_question(self, pamar):
        sql = "INSERT INTO [tb_FreeQuestion] (ID,UserName,UserHeadUrl,Content,CreateTime,ProvinceCode,CityCode,FIID,IsDel,QFrom) "
        sql += " VALUES(%s,%s,%s,%s, %s,%s,%s,%s,0,0)"
        self.con.exec_no_query(sql, pamar)

   #添加回答
    def insert_free_reply(self, pamar):
        sql = "INSERT INTO [tb_Reply] (ID,UIID,Content,QID,RID,CreateTime,IsDel) "
        sql += " VALUES(%s,%s,%s,%s,%s,%s,%d)"
        self.con.exec_no_query(sql, pamar)