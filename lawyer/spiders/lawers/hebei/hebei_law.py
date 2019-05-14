#!/usr/bin/python
#-*- coding: utf-8 -*-
import pymongo
import os
import platform
import sys

def open_excel(filename):
    try:
        return xlrd.open_workbook(filename)
    except Exception,e :
        raise e

 #根据索引获取Excel表格中的数据   参数:file：Excel文件路径     colnameindex：表头列名所在行的索引  ，by_index：表的索引
def excel_table_byindex(file,colnameindex=0,by_index=0):
     data = open_excel(file)
     table = data.sheets()[by_index]
     nrows = table.nrows #行数
     ncols = table.ncols #列数
     list =[]
     for rownum in range(1,nrows):
        row = table.row_values(rownum)
        if row:
              app = {}
              colnames = table.row_values(colnameindex)  # 某一行数据
              for i in range(len(colnames)):
                 app[colnames[i]] = row[i]
              list.append(app)
     return list

 #根据名称获取Excel表格中的数据   参数:file：Excel文件路径     colnameindex：表头列名所在行的索引  ，by_name：Sheet1名称
def excel_table_byname(file ,colnameindex=0,by_name=u'Sheet1'):
     data = open_excel(file)
     table = data.sheet_by_name(by_name)
     nrows = table.nrows #行数
     colnames =  table.row_values(colnameindex) #某一行数据
     list =[]
     for rownum in range(1,nrows):
          row = table.row_values(rownum)
          if row:
              app = {}
              for i in range(len(colnames)):
                 app[colnames[i]] = row[i]
              list.append(app)
     return list

class MogodbHelper(object):

    def __init__(self, mongo_uri, mongo_db, mongo_replicat_set, mongo_username, mongo_password):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_replicat_set = mongo_replicat_set
        self.mongo_username = mongo_username
        self.mongo_password = mongo_password

    def open(self):
        self.client = pymongo.MongoClient(self.mongo_uri,replicaSet=self.mongo_replicat_set)
        self.client[self.mongo_db].authenticate(self.mongo_username, self.mongo_password)
        self.db = self.client[self.mongo_db]

    def close(self):
        self.client.close()

    def add_item(self, item):
        if dict(item).has_key('collection'):
            model = dict(item)
            del model['collection']
            self.db[item["collection"]].insert(model)
def main():
    mongo=MogodbHelper(mongo_uri=MONGO_URI,mongo_db=MONGO_DATABASE,mongo_replicat_set=MONGO_REPLICAT_SET,mongo_username=MONGO_USERNAME,mongo_password=MONGO_PASSWORD)
    try:
        mongo.open()
        data=excel_table_byindex(filepath)
        for row in data:
            if row['name']!='':
                mongo.add_item(convertItem(row))
    except Exception as e :
        print 'Execution failure'
        mongo.close()
        raise  e
    finally:
        print 'Execution success'
        mongo.close()

def convertItem(item):
        personnel_type1 = item['personnel_type1']
        personnel_type2 = item['personnel_type2']
        del item['personnel_type1']
        del item['personnel_type2']
        if personnel_type1 != '':
            item['personnel_type'] = u'专职律师'
        if personnel_type2 != '':
            item['personnel_type'] = u'兼职律师'
        if item['sex'] == u'男':
            item['sex'] = 0
        elif item['sex'] == u'女':
            item['sex'] = 1
        else:
            item['sex'] = ''
        item['firm']=str(item['firm']).replace(' ','')
        item['start_time'] = convertDate(str(item['start_time']))
        item['url']=''
        item['political_status'] = ''
        item['profession'] = ''
        item['professional_status'] = ''
        item['get_time'] = ''
        item['nation'] = ''
        item['cert_type'] = ''
        item['headurl'] = ''
        item['ispartnership'] = ''
        item['collection'] = 'lawyers'
        item['province'] = u'河北'
        return item
def convertDate(s):
    if s!='' or s!=None:
        s = s.replace(u'年','-').replace(u'月','-').replace(u'日','').replace('.','-').replace(' ','')
        count =s.count('-')
        if count==0:
           s ='%s-01-01' % s
        elif count ==1:
           s = '%s-01' % s
        return s

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')
    import xlrd
    '''河北律师导入mongodb'''
    sysstr = platform.system()
    if (sysstr == "Windows"):
        MONGO_URI = 'mongodb://127.0.0.1:27017'
        MONGO_DATABASE = 'spider'
        MONGO_REPLICAT_SET = None
        MONGO_USERNAME = 'lvhe'
        MONGO_PASSWORD = 'lvhe123'
    elif (sysstr == "Linux"):
        MONGO_URI = ["dds-m5ee1e049673a1541.mongodb.rds.aliyuncs.com:3717",
                     "dds-m5ee1e049673a1542.mongodb.rds.aliyuncs.com:3717"]
        MONGO_DATABASE = 'spider'
        MONGO_REPLICAT_SET = "mgset-2808337"
        MONGO_USERNAME = 'lvhe'
        MONGO_PASSWORD = 'lvhe1q2w3e4r'
    filepath = os.path.abspath(u'河北律师.xls')
    main()


