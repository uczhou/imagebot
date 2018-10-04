from scrapy.spiders import CrawlSpider
from scrapy.http import Request
from scrapy.selector import Selector
from ..items import ImageItem, SrcItem, MetaItem
from ..config import default_headers, file_folder, image_folder, screenshot_folder, classid, source_name
import re
import logging
from ..utils import createFolder
import hashlib

import requests
import time
from selenium import webdriver
import execjs
import json
from urllib.parse import urlencode


class ImagebotSpider(CrawlSpider):

    name = "imagespider"

    createFolder(file_folder)
    createFolder(image_folder)
    createFolder(screenshot_folder)

    t = int(time.time())

    # Log file
    log_path = "{}/log_{}.txt".format(file_folder, t)

    logging.basicConfig(
        filename=log_path,
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        level=logging.DEBUG,
        filemode='a'
    )

    logger = logging.getLogger(__name__)

    allowed_domains = ["toutiao.com", "pstatp.com", "weibo.cn", "weibo.com", "sinaimg.cn"]

    parsed = set()
    scraped = set()

    user_id = 98011335869
    media_id = 1599501878996996

    def start_requests(self):
        urls = []
        for url in urls:
            yield Request(url, headers=default_headers,
                          meta={"dont_retry": False, "max_retry_times": 3, "selenium": 3, "user_id": self.user_id, "max_behot_time": 0}, callback=self.parse)

    def get_weibo_url(self, n):
        data = {
            'containerid': '1078032167446614_-_photoall',
            'page': n,
            'count':24,
            'title': '图片墙',
            'luicode': '10000011',
            'lfid': '1078032167446614'
        }

        url = 'https://m.weibo.cn/p/second?' + urlencode(data)

        return url

    def get_toutiao_url(self, user_id, media_id, t, signature=False):

        if signature:
            data = {
                'page_type': 1,
                'user_id': user_id,
                'max_behot_time': t,
                'count': 20,
                'as': '',
                'cp': '',
                '_signature': '0'
            }

            ascp = self.py_execjs()
            data['as'] = ascp['as']
            data['cp'] = ascp['cp']

            url = 'https://www.toutiao.com/c/user/article/?' + urlencode(data)

        else:
            data = {
                "page_type": 1,
                "max_behot_time": "",
                "uid": user_id,
                "media_id": media_id,
                "output": "json",
                "is_json": 1,
                "count": 20,
                "from": "user_profile_app",
                "version": 2,
                "as": "",
                "cp": "",
                "callback": "jsonp3"
            }

            data["max_behot_time"] = t

            ascp = self.py_execjs()
            data['as'] = ascp['as']
            data['cp'] = ascp['cp']

            url = 'https://www.toutiao.com/pgc/ma/?' + urlencode(data)

        return url

    def parse(self, response):
        print(response.url)

        hxs = Selector(response)

        # mobile end version
        # json file parser
        if re.match('https://www.toutiao.com/pgc/ma/', response.url):

            data = response.body_as_unicode().split("(")[1].strip(")")

            result_json = json.loads(data)

            has_more = result_json['has_more']

            if has_more or has_more == 1:

                max_behot_time = result_json['next']['max_behot_time']

                yield Request(self.get_toutiao_url(self.user_id, self.media_id, max_behot_time), headers=default_headers,
                              meta={"dont_retry": False, "max_retry_times": 3, "selenium": 5}, callback=self.parse)

                time.sleep(5)

            if result_json['message'] == 'success':

                cards = result_json['data']

                for i in range(len(cards)):

                    title = cards[i]['title']

                    images = cards[i]['image_detail']

                    info = cards[i]['abstract']

                    referer = cards[i]['display_url']

                    pid = cards[i]['item_id']

                    meta_item = self.get_meta_item(pid, info, title, classid, source_name)

                    yield meta_item

                    image_item = self.get_image_item(pid, referer, classid, source_name)

                    for image in images:

                        url = image['url']

                        image_item['image_urls'].append(url)

                        src_item = self.get_src_item(pid, referer, classid, source_name)

                        src_item['image_url'] = url

                        yield src_item

                    yield image_item

        elif re.match('https://www.toutiao.com/[a|i]', response.url):

            links = hxs.xpath('//div[@class="imageList"]/ul/li')

            articles = hxs.xpath('//div[@class="article-box"]/div[@class="article-content"]/div/div')

            if len(links) > 0:

                title = ' '.join(hxs.xpath('//title/text()').extract())

                pid = response.url.split('/')[-2]
                image_item = self.get_image_item(pid, response.url, classid, source_name)

                meta_item = self.get_meta_item(pid, title, title, classid, source_name)

                for link in links:

                    href = link.xpath('.//div[@class="image-item-inner"]/a/@href').extract_first()

                    image_item['image_urls'].append(href)

                    src_item = self.get_src_item(pid, response.url, classid, source_name)

                    src_item['image_url'] = href

                    yield src_item

                yield meta_item
                yield image_item

            elif len(articles) > 0:

                title = ' '.join(hxs.xpath('//title/text()').extract())

                pid = response.url.split('/')[-2]

                image_item = self.get_image_item(pid, response.url, classid, source_name)

                meta_item = self.get_meta_item(pid, title, title, classid, source_name)

                for link in articles:

                    href = link.xpath('.//img/@src').extract_first()

                    image_item['image_urls'].append(href)

                    src_item = self.get_src_item(pid, response.url, classid, source_name)
                    src_item['image_url'] = href

                    yield src_item

                yield meta_item
                yield image_item

        # desktop end
        # json file parser
        elif re.match('https://www.toutiao.com/c/user/', response.url):

            data = response.body_as_unicode()

            result_json = json.loads(data)

            print(result_json['message'])

            if result_json['message'] == 'success':

                cards = result_json['data']

                for i in range(len(cards)):
                    url = cards[i]['display_url']
                    href = 'https:' + url

                    yield Request(href, headers=default_headers,
                                 meta={"dont_retry": False, "max_retry_times": 3}, callback=self.parse)

            has_more = result_json['has_more']

            if has_more or has_more == 1:
                max_behot_time = result_json['next']['max_behot_time']

                yield Request(response.url, meta={"dont_retry": False, "max_retry_times": 3, "selenium": 1,
                                                  "user_id": self.user_id, "max_behot_time": max_behot_time},
                              callback=self.parse)

        # Use chrome to scroll the page
        elif re.match('https://m.toutiao.com/profile/', response.url):
            print(response.url)

            links = hxs.xpath('//div[@class="list-content feed dongtai"]/div')

            for link in links:

                href = link.xpath('//div[@class="item-body"]/div[@class="dyitem-article js-group-item"]/@data-id').extract()

                for src in href:
                    src = "https://www.toutiao.com/item/" + src

                    src_md5 = hashlib.sha1(src.encode('utf-8')).hexdigest()
                    if src not in self.parsed and src_md5 not in self.scraped:
                        print(src)

                        yield Request(url=src, headers=default_headers, meta={"dont_retry": False, "max_retry_times": 3,
                                                                              "selenium": 0}, callback=self.parse)
                    self.parsed.add(src)

        elif re.match('https://m.weibo.cn/api/container', response.url):

            result_json = json.loads(response.body_as_unicode())

            cards = result_json['data']['cards']

            image_item = self.get_image_item('', response.url, classid, source_name)

            image_item['cookies'] = response.cookies

            for i in range(len(cards)):

                if 'pics' in cards[i]:
                    pics = cards[i]['pics']

                    for pic in pics:

                        mblog = pic['mblog']
                        if mblog:
                            mid = mblog['mid']
                            text = mblog['text']
                            if image_item['pid'] == '':
                                image_item['image_urls'].append(pic['pic_big'])
                                image_item['pid'] = mid
                                meta_item = self.get_meta_item(mid, text, text, classid, source_name)

                                yield meta_item

                            elif image_item['pid'] == mid:
                                image_item['image_urls'].append(pic['pic_big'])

                            else:
                                yield image_item

                                image_item = self.get_image_item(mid, response.url, classid, source_name)

                                image_item['image_urls'].append(pic['pic_big'])

                                image_item['cookies'] = response.cookies

                                meta_item = self.get_meta_item(mid, text, text, classid, source_name)

                                yield meta_item

                            src_item = self.get_src_item(mid, response.url, classid, source_name)

                            src_item['image_url'] = pic['pic_big']

                            yield src_item
            yield image_item

            pageno = result_json['data']['cardlistInfo'].get('page')
            if pageno:
                yield Request(self.get_weibo_url(pageno), headers=default_headers,
                              meta={"dont_retry": False, "dont_redirect": True, "max_retry_times": 3, 'selenium': 2})

    def get_signature(self, user_id, max_behot_time):

        req = requests.Session()

        jsurl = 'https://s3.pstatp.com/toutiao/resource/ntoutiao_web/page/profile/index_591a490.js'
        resp = req.get(jsurl)
        js = resp.content.decode()
        effect_js = js.split("Function")

        js = 'var navigator = {}; navigator["userAgent"] = "Mozilla/5.0 (Windows NT 6.1; WOW64) ' \
             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36";' + "Function" + \
             effect_js[3] + "Function" + effect_js[4] + ";function result(){ return TAC.sign(" + \
             str(user_id)  +  str(max_behot_time) +");} return result();"

        # driver used to execute js
        driver = webdriver.Chrome("/Users/hongleizhou/webdocs/SOPs/tools/chromedriver")

        output = driver.execute_script(js)

        driver.quit()
        return output

    def md5_encrypt(self):
        t = int(time.time())
        m = hashlib.md5()
        m.update(str(t).encode(encoding='utf8'))
        return m.hexdigest()

    def py_execjs(self):
        node = execjs.get()
        file = '/Users/hongleizhou/webdocs/toutiao/toutiao.js'
        content = open(file, encoding='utf-8', errors='ignore').read()
        ctx = node.compile(content)
        js = 'getHoney()'
        result = ctx.eval(js)
        return result

    def get_image_item(self, pid, url, classid, source_name):
        image_item = ImageItem()
        image_item['image_urls'] = []
        image_item['referer'] = url
        image_item['pid'] = pid
        image_item['classid'] = classid
        image_item['source_name'] = source_name

        return image_item

    def get_meta_item(self, pid, info, name, classid, source_name):
        meta_item = MetaItem()
        meta_item['pid'] = pid
        meta_item['info'] = info
        meta_item['name'] = name
        meta_item['classid'] = classid
        meta_item['source_name'] = source_name

        return meta_item

    def get_src_item(self, pid, url, classid, source_name):
        src_item = SrcItem()
        src_item['pid'] = pid
        src_item['referer'] = url

        # src_item['image_url'] = href
        src_item['classid'] = classid
        src_item['source_name'] = source_name

        return src_item