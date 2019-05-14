#!/usr/bin/python
# -*- coding: utf-8 -*-
from dal.com.MSSQLBasic import MSSQLBasic

'''
author:dl
date:2018/9/3
desc:操作法律知识
'''


class LawKnowData(MSSQLBasic):

    # 插入菜单
    def insert_lawknow_menu(self, pamar):
        sql = "INSERT INTO tb_LawKnowMenu (ID, Name,ParentId)  VALUES (%s, %s, %s)"
        self.con.exec_no_query(sql, pamar)

    def query_lawknow_menu_one(self,pamar):
        sql='select id from  tb_LawKnowMenu  where parentid is null and Name = %s'
        return self.con.exec_query_one(sql,pamar)

    def query_lawknow_sub_menu_one(self, pamar):
        sql = 'select id from  tb_LawKnowMenu  where parentid is not null and Name= %s'
        return self.con.exec_query_one(sql,pamar)

    def query_exists_lawknow_by_url(self, pamar):
        sql = 'select id from  tb_LawKnow  where url= %s'
        return self.con.exec_query_one(sql, pamar)

    # 添加法律知识
    def insert_lawkno(self, pamar):
        sql = "INSERT INTO tb_LawKnow (ID, Title,Content,MenuId,PubDate,BrowCount,Source,Url)  VALUES (%s, %s,%s,%s,%s,%d,%s,%s)"
        self.con.exec_no_query(sql, pamar)
