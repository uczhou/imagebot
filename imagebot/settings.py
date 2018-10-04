# -*- coding: utf-8 -*-

from .config import image_folder

BOT_NAME = 'GoogleBot'

SPIDER_MODULES = ['imagebot.spiders']
NEWSPIDER_MODULE = 'imagebot.spiders'

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.54 Safari/536.5'

ITEM_PIPELINES = {
    # Enable MongodbPipeline and Disable ImagebotPipeline, ImagePathPipeline if save info into mongodb
    'imagebot.pipelines.ImagebotPipeline': 1,
    'imagebot.pipelines.ImageDownloadPipeline': 2,
    'imagebot.pipelines.ImagePathPipeline': 3,
    # 'imagebot.pipelines.MongodbPipeline': 4
}

DOWNLOADER_MIDDLEWARES = {
    'imagebot.middlewares.ImagebotJSMiddleware': 543
    # 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
}

IMAGES_STORE = image_folder

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 5

DOWNLOAD_DELAY = 5

# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 5
CONCURRENT_REQUESTS_PER_IP = 5
