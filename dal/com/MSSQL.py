#!/usr/bin/python
#-*- coding: utf-8 -*-
import pymssql

class MSSQL:

    def __init__(self,host,user,pwd,db):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db

    def get_connection(self):
        if not self.db:
            raise(NameError,'没有设置数据库信息')
        self.conn = pymssql.connect(host=self.host,user=self.user,password=self.pwd,database=self.db,charset='utf8')
        cur = self.conn.cursor()
        if not cur:
            raise (NameError,'连接数据库失败')
        else:
            return cur

    def exec_query(self,sql,params=None):
        cur = self.get_connection()
        cur.execute(sql,params)
        res_list = cur.fetchall()
        self.conn.close()
        return  res_list

    def exec_query_one(self, sql, params=None):
        cur = self.get_connection()
        cur.execute(sql, params)
        row = cur.fetchone()
        self.conn.close()
        return row

    def exec_no_query(self,sql,params=None):
        cur = self.get_connection()
        cur.execute(sql,params)
        self.conn.commit()
        self.conn.close()



    def exec_many_non_query(self,sql,params=None):
        cur = self.get_connection()
        cur.executemany(sql, params)
        self.conn.commit()
        self.conn.close()
