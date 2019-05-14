#!/usr/bin/python
#-*- coding: utf-8 -*-
import os


BOT_NAME = 'lawyer'
SPIDER_MODULES = ['lawyer.spiders']
NEWSPIDER_MODULE = 'lawyer.spiders'

spider_env=os.getenv("SPIDER_ENV", "dev")
#生产环境配置
if spider_env == "product":
    from lawyer.settings.product import *
#开发环境配置
else :
    from lawyer.settings.dev import *







