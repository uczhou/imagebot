import scrapy
from scrapy import Field


class ImagebotItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class TagItem(scrapy.Item):
    classid = Field()
    number = Field()
    tags = Field()
    model = Field()
    co = Field()
    link = Field()
    title = Field()


class MetaItem(scrapy.Item):
    classid = Field()
    source_name = Field()
    name = Field()
    pid = Field()
    info = Field()
    album = Field()
    time = Field()


class ImageItem(scrapy.Item):
    classid = Field()
    source_name = Field()
    image_urls = Field()
    images = Field()
    image_paths = Field()
    referer = Field()
    pid = Field()
    retry = Field()
    cookies = Field()


class SrcItem(scrapy.Item):
    classid = Field()
    source_name = Field()
    pid = Field()
    referer = Field()
    image_url = Field()


class PathItem(scrapy.Item):
    classid = Field()
    source_name = Field()
    pid = Field()
    image_url = Field()
    path_url = Field()


class ScrapedItem(scrapy.Item):
    source_name = Field()
    url_md5 = Field()