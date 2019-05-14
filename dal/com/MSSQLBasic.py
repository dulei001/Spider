# coding=utf-8
from dal.com.MSSQL import MSSQL


class MSSQLBasic:
    def __init__(self):
        self.con = MSSQL(host='192.168.2.4',user='LvKe',pwd="LvKe!Q@W#E$R",db='LvKe')

