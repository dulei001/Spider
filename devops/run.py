#!/usr/bin/python
#-*- coding: utf-8 -*-
import os
import  scrapyd_deploy
import  scrapyd_scheduling
import scrapyd_cencel
from scrapy.utils.conf import get_config, closest_scrapy_cfg

from devops import util

def main():
     #部署整个工程
    scrapyd_deploy.deploy()
     #运行spider
    scrapyd_scheduling.schedule(project="lawyer", spider="beijing_lawyer_spider")
    # 取消运行spder 执行二次
    #scrapyd_cencel.cancel(project="lawyer",job="088b5b6cf75111e6af2b0242c0a80004")
    pass


if __name__ == "__main__":
    main()

