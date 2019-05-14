#!/usr/bin/python
# -*- coding: utf-8 -*-
from dal.com.MSSQLBasic import MSSQLBasic

'''
author:dl
date:2018/11/16
desc:华律合同名库菜单
'''


class ContractMenuData(MSSQLBasic):

    # 插入菜单
    def insert_contract_menu(self, pamar):
        sql = "INSERT INTO tb_ContractMenu (ID, Name,PID,Sort,IsDel)  VALUES (%s, %s, %s,%d,%d)"
        self.con.exec_no_query(sql, pamar)

    # 添加合同
    def insert_contract(self, pamar):
        sql = "INSERT INTO tb_Contract (CID, ContractMenuId,Content,Title,Createtime,Url,IsReserve,DownloadCount,ViewCount) " \
                               " VALUES (%s, %s,%s,%s, %s,%s,%d,%d,%d)"
        self.con.exec_no_query(sql, pamar)
