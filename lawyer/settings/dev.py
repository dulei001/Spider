#!/usr/bin/python
#-*- coding: utf-8 -*-
import logging

ROBOTSTXT_OBEY = False
COOKIES_DEBUG=False
COOKIES_ENABLED=True
#负数表示路径越深优先级越高
DEPTH_PRIORITY=-1
CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 8
AUTOTHROTTLE_ENABLED = False

#重试中间件配置
RETRY_ENABLED=True
RETRY_TIMES=50
RETRY_HTTP_CODES=[500, 502, 503, 504, 408,429]
RETRY_PRIORITY_ADJUST=-15
REDIRECT_ENABLED=True

#默认请求头
DEFAULT_REQUEST_HEADERS={
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Language': 'zh-CN,zh;q=0.8',
'Connection':'keep-alive'
}

ITEM_PIPELINES = {
    'lawyer.pipelines.json_writer_pipeline.JsonWriterPipeline': 1,
   # 'lawyer.pipelines.fagui_writer_mmsql_pipeline.FaGuiWriterPipeline': 1,
    #'lawyer.pipelines.laywer_writer_mmsql_pipeline.LawyerWriterPipeline': 0,
    #'lawyer.pipelines.mongo_pipeline.MongoPipeline':0
}

DOWNLOADER_MIDDLEWARES = {
    # Engine side
    'scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware': 100,
    'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': 300,
    'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware': 350,
    'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware': 400,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 500,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
    'scrapy.downloadermiddlewares.ajaxcrawl.AjaxCrawlMiddleware': 560,
    'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': 580,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 590,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': 600,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 700,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750,
    'scrapy.downloadermiddlewares.stats.DownloaderStats': 850,
    'scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware': 900,
    # Downloader side
    'lawyer.middlewares.rotate_user_agent_middleware.RotateUserAgentMiddleware': 950,
    #'lawyer.middlewares.proxy_middleware.ProxyMiddleware': 960
}

# 下载速度控制
RANDOMIZE_DOWNLOAD_DELAY = True
DOWNLOAD_DELAY = 2
DOWNLOAD_TIMEOUT = 500

DUPEFILTER_DEBUG = True
MONGO_URI = ["192.168.1.6:27017"]
MONGO_DATABASE = 'spider'
MONGO_REPLICAT_SET=None
MONGO_USERNAME = 'spider'
MONGO_PASSWORD = 'spider'

REDIS_HOST="139.129.96.112"
REDIS_PORT="6379"

CONVERT_JOSN_URL="http://139.129.96.112:6901/json/convert"

