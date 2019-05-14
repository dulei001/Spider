#!/usr/bin/python
#-*- coding: utf-8 -*-
import hashlib
import os
import random
import string
import urllib

from scrapy.utils.python import to_bytes


def multpart_encode(form_data):
    _boundary = to_bytes(''.join(
        random.choice(string.digits + string.ascii_letters) for i in range(20)))
    content_type = "multipart/form-data; boundary=" + _boundary

    body = []
    for name, value in form_data.items():
        body.append(b'--' + _boundary)
        body.append(b'Content-Disposition: form-data; name="' + to_bytes(name) + b'"')
        body.append(b'')
        body.append(to_bytes(value))

    body.append(b'--' + _boundary + b'--')

    return content_type, b'\r\n'.join(body)


    # 图片存储路径

#项目目录
IMAGE_STORG = os.path.abspath('/data/spider')
#资源文件夹
IMAGE_NAME = 'files'

# 下载详细图片
# urls图片链接集合 dirname文件夹名称
def downloadImage(urls, dirname=None):
    data = []
    if len(urls) > 0:
        if IMAGE_STORG != '':
            if dirname != None:
                dir_path = '%s/%s/%s' % (IMAGE_STORG, IMAGE_NAME, dirname)
            else:
                dir_path = '%s/%s' % (IMAGE_STORG, IMAGE_NAME)
        else:
            raise Exception('IMAGE_STORG is empty')
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        for url in urls:
            try:
                file_name = hashlib.sha1(
                    to_bytes(url)).hexdigest() + '.jpg'  # change to request.url after deprecation
                file_path = os.path.join(dir_path, file_name)  #
                urllib.urlretrieve(url, file_path)
                if dirname != None:
                    savename = '%s/%s' % (dirname, file_name)
                else:
                    savename = '/%s%s' % (IMAGE_NAME, file_name)
                data.append(savename)
            except  Exception as e:
                print "error imageUrl is :%s" % url
    return data

'''有时我们会碰到类似下面这样的 unicode 字符串: u\xe4\xbd\xa0\xe5\xa5\xbd
       python 提供了一个特殊的编码（ raw_unicode_escape ）用来处理这种情况'''
def unicodeParseStr(s):
    return s.replace('\r', '').replace('\n', '').encode('raw_unicode_escape').decode('gbk')