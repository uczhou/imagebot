import json
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy import Request
from .items import MetaItem, SrcItem, TagItem, ImageItem, PathItem
from .config import meta_path, src_path, image_path, tag_path, image_folder, \
    file_folder, screenshot_folder, default_headers, db_settings
import os
import hashlib
from urllib.parse import urlparse
import pymongo

crawled = set()
if os.path.exists('{}/full'.format(image_folder)):
    files = os.listdir('{}/full'.format(image_folder))
    for file in files:
        crawled.add(file.split('.')[0])


class ImagebotPipeline(object):

    def __init__(self):

        if not os.path.exists(image_folder):
            try:
                os.makedirs(image_folder)
            except OSError:
                print("Creation of the directory {} failed".format(image_folder))

        if not os.path.exists(screenshot_folder):
            try:
                os.makedirs(screenshot_folder)
            except OSError:
                print("Creation of the directory {} failed".format(screenshot_folder))

        if not os.path.exists(file_folder):
            try:
                os.makedirs(file_folder)
            except OSError:
                print("Creation of the directory {} failed".format(file_folder))

        self.meta_file = open(meta_path, 'a+')
        self.src_file = open(src_path, 'a+')
        self.tag_file = open(tag_path, 'a+')

    def close_spider(self, spider):
        self.meta_file.close()
        self.src_file.close()
        self.tag_file.close()

    def process_item(self, item, spider):
        if isinstance(item, MetaItem):
            line = json.dumps(dict(item)) + "\n"
            print(line)
            self.meta_file.write(line)
            self.meta_file.flush()

            raise DropItem("In LindabotPipeline: Finished Processing Meta Item: {}".format(line))

        elif isinstance(item, SrcItem):
            line = json.dumps(dict(item)) + "\n"
            print(line)
            self.src_file.write(line)
            self.src_file.flush()

            raise DropItem("In LindabotPipeline: Finished Processing Src Item: {}".format(line))
        elif isinstance(item, TagItem):
            line = json.dumps(dict(item)) + "\n"
            print(line)
            self.tag_file.write(line)
            self.tag_file.flush()

            raise DropItem("In LindabotPipeline: Finished Processing Tag Item: {}".format(line))
        else:
            return item


class ImageDownloadPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        if isinstance(item, ImageItem):
            for image_url in item['image_urls']:
                sha1_name = hashlib.sha1(image_url.encode('utf-8')).hexdigest()
                if sha1_name not in crawled:
                    default_headers['Referer'] = item['referer']
                    default_headers['Host'] = urlparse(image_url).netloc
                    if item['cookies']:
                        default_headers['Cookie'] = item['cookies']
                    yield Request(image_url, headers=default_headers,
                                  meta={"dont_retry": False, "dont_redirect": True, "max_retry_times": 3})
    def item_completed(self, results, item, info):
        if isinstance(item, ImageItem):
            image_paths = [{x['url']: x['path'].split('/')[-1]} for ok, x in results if ok]
            if not image_paths:
                raise DropItem("In ImageDownloadPipeline: Image Item contains no images")
            item['image_paths'] = image_paths
        print("item_completed: {}".format(item))
        return item


class ImagePathPipeline(object):

    def __init__(self):

        self.imagepath_file = open(image_path, 'a+')

    def close_spider(self, spider):
        self.imagepath_file.close()

    def process_item(self, item, spider):
        if not item['image_paths']:
            raise DropItem("In ImagePathPipeline: Image Item contains no image path")

        for path in item['image_paths']:
            line = json.dumps(dict(path)) + "\n"
            print(line)
            self.imagepath_file.write(line)
            self.imagepath_file.flush()


class MongodbPipeline(object):

    def __init__(self):
        connection = pymongo.MongoClient(
            db_settings['MONGODB_SERVER'],
            db_settings['MONGODB_PORT']
        )

        db = connection[db_settings['MONGODB_DB']]
        self.meta_collection = db[db_settings['MONGODB_META_COLLECTION']]
        self.source_collection = db[db_settings['MONGODB_SOURCE_COLLECTION']]
        self.path_collection = db[db_settings['MONGODB_PATH_COLLECTION']]
        self.tags_collection = db[db_settings['MONGODB_TAGS_COLLECTION']]

    def process_item(self, item, spider):
        if isinstance(item, MetaItem):
            self.meta_collection.insert(dict(item))
            raise DropItem("In Mongodb Pipeline: Finished Processing Meta Item: {}".format(dict(item)))

        elif isinstance(item, SrcItem):
            self.source_collection.insert(dict(item))
            raise DropItem("In Mongodb Pipeline: Finished Processing Src Item: {}".format(dict(item)))

        elif isinstance(item, TagItem):
            self.tags_collection.insert(dict(item))
            raise DropItem("In Mongodb Pipeline: Finished Processing Tag Item: {}".format(dict(item)))
        elif isinstance(item, ImageItem):
            if not item['image_paths']:
                raise DropItem("In Mongodb Pipeline: Image Item contains no image path")
            for path in item['image_paths']:
                path_item = PathItem()

                path_item['pid'] = item['pid']
                path_item['classid'] = item['classid']
                path_item['source_name'] = item['source_name']
                for key, value in path.items():
                    path_item['image_url'] = key
                    path_item['path_url'] = value

                self.path_collection.insert(dict(path_item))
            raise DropItem("In Mongodb Pipeline: Finished Processing Image Item: {}".format(dict(item)))