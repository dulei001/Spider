#!/usr/bin/python
# -*- coding: utf-8 -*-
from dal.com.MSSQLBasic import MSSQLBasic
'''
author:dl
date:2018/9/3
desc:操作省市
'''
class AreaData(MSSQLBasic):

    def find_area_by_name_return_code(self, pamar):
        sql = "select Code from  tb_Area  where  Name =  %s"
        return self.con.exec_query_one(sql, pamar)


