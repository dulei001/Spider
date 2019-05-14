#!/usr/bin/python
#-*- coding: utf-8 -*-
'''ID	Name
08410fe3-d3df-474f-b480-1dd4e9000e99	合同纠纷
0e806288-7728-4fdb-9e39-575ec25b7194	房产纠纷
0f394b66-027a-4d17-8027-cd581875d454	劳动人事
36f8e3ba-6a64-49ac-acde-cd75c867ae2e	刑事案件
3bca3ba1-622c-4c4a-ba84-b19c121cc593	婚姻家庭
49bd63e8-7dff-4cb8-8b4e-c3aa1ffd45b8	遗产继承
7b083fa5-ee63-4189-a99d-27099585f3a4	损害赔偿
7d625380-dd34-4ad4-9d23-bffba42522e3	交通事故
9c96df1d-34ad-47f6-8aab-3faebf045902	涉外业务
a4d27475-59c6-4a0f-9577-1eac701b39c6	医疗纠纷
bbde3980-0f83-4b43-8c90-6d3fd1e6b544	征收拆迁
c01d5861-3bdf-46ea-ae3f-46acab4e8021	投融资
d5efea46-377b-4bda-a6fe-3cb1d6617c15	行政诉讼
e529a00f-d1aa-4a0d-9c89-46041db09a61	债权债务
f255f0d9-aadd-4a3c-b559-86c5afcab1ae	消费维权'''
field_dic=[
{'id':'08410fe3-d3df-474f-b480-1dd4e9000e99','name':u'合同纠纷'},
{'id':'0e806288-7728-4fdb-9e39-575ec25b7194','name':u'房产纠纷'},
{'id':'0f394b66-027a-4d17-8027-cd581875d454','name':u'劳动人事'},
{'id':'36f8e3ba-6a64-49ac-acde-cd75c867ae2e','name':u'刑事案件'},
{'id':'3bca3ba1-622c-4c4a-ba84-b19c121cc593','name':u'婚姻家庭'},
{'id':'49bd63e8-7dff-4cb8-8b4e-c3aa1ffd45b8','name':u'遗产继承'},
{'id':'7b083fa5-ee63-4189-a99d-27099585f3a49','name':u'损害赔偿'},
{'id':'7d625380-dd34-4ad4-9d23-bffba42522e3','name':u'交通事故'},
{'id':'9c96df1d-34ad-47f6-8aab-3faebf045902','name':u'涉外业务'},
{'id':'a4d27475-59c6-4a0f-9577-1eac701b39c6','name':u'医疗纠纷'},
{'id':'bbde3980-0f83-4b43-8c90-6d3fd1e6b544','name':u'征收拆迁'},
{'id':'c01d5861-3bdf-46ea-ae3f-46acab4e8021','name':u'投融资'},
{'id':'d5efea46-377b-4bda-a6fe-3cb1d6617c15','name':u'行政诉讼'},
{'id':'e529a00f-d1aa-4a0d-9c89-46041db09a61','name':u'债权债务'},
{'id':'f255f0d9-aadd-4a3c-b559-86c5afcab1ae','name':u'消费维权'},
]

def find_field_by_name(names):
     resultarr=[]
     for item in field_dic:
        for name in names:
           if item['name'] ==name:
               resultarr.append(item['id'])
     return  resultarr