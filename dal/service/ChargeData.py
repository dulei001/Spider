#!/usr/bin/python
# -*- coding: utf-8 -*-
from dal.com.MSSQLBasic import MSSQLBasic

'''
author:dl
date:2018/9/3
desc:操作罪名库
'''


class ChargeData(MSSQLBasic):

    # 插入菜单
    def insert_charge_menu(self, pamar):
        sql = "INSERT INTO tb_ChargeMenu (ID, Name,ParentId)  VALUES (%s, %s, %s)"
        self.con.exec_no_query(sql, pamar)

    # 添加罪名苦
    def insert_charge(self, pamar):
        sql = "INSERT INTO tb_Charge (ID, Title,Content,MenuId,ChargeForm)  VALUES (%s, %s,%s,%s,%d)"
        self.con.exec_no_query(sql, pamar)
