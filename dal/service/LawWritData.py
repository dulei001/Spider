#!/usr/bin/python
# -*- coding: utf-8 -*-
from dal.com.MSSQLBasic import MSSQLBasic

class LawWritData(MSSQLBasic):

    # 插入菜单
    def insert_lawwrit_menu(self, pamar):
        sql = "insert into tb_LawWritMenu(ID,Name,Sort,IsDel) values(%s,%s,%d,%d)"
        self.con.exec_no_query(sql, pamar)


    # 添加文书
    def insert_lawwrit(self, pamar):
        sql = "insert into tb_LawWrit([ID],[MenuId],[Content],[Title],[Createtime],[Url],[DownloadCount],[ViewCount]) values(%s,%s,%s,%s,%s,%s,%d,%d) "
        self.con.exec_no_query(sql, pamar)
