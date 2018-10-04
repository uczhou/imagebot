from scrapy import signals
from selenium import webdriver
from scrapy.http import HtmlResponse
import time
from .config import screenshot_folder
from .utils import createFolder
from selenium.common.exceptions import TimeoutException
import signal
import random
from urllib.parse import urlencode


class ImagebotSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ImagebotDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ImagebotJSMiddleware(object):

    requests_headers = {
        "Accept": "application/json, text/javascript",
        'Accept-Encoding': 'gzip, deflate, br',
        "Accept-Language": "en-US,en;q=0.9",
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'max-age=0',
        "Connection": "keep-alive",
        "Cookie": 'tt_webid=6606897633125369358; WEATHER_CITY=%E5%8C%97%E4%BA%AC; UM_distinctid=166291f9f67520-0f6faab8277d55-346a7809-232800-166291f9f6856; CNZZDATA1259612802=48565978-1538287942-%7C1538287942; tt_webid=6606897633125369358; __tasessionId=q4wgcj1511538288230545; csrftoken=c6150e40ca4db609f0ee5ab4649eff4b; uuid="w:1e61cd595a584bbf88b1426d3ff5abf6"',
        "Host": 'www.toutiao.com',
        'Referer': 'https://www.toutiao.com/c/user/98011335869/',
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
    }

    # Single Thread
    def __init__(self):
        # self.driver = webdriver.PhantomJS()

        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')

        # mobile end emulation

        # options.add_argument('--headless')

        # options.add_argument('user-agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"')

        # mobile_emulation = {"deviceName": "Nexus 5"}

        # options.add_experimental_option("mobileEmulation", mobile_emulation)

        self.driver = webdriver.Chrome(executable_path = '/Users/hongleizhou/webdocs/SOPs/tools/chromedriver', options=options)

        timeout = 40
        self.driver.set_page_load_timeout(timeout)
        self.driver.implicitly_wait(timeout)

        t = int(time.time())

        self.screenshot_sub_folder = '{}/{}'.format(screenshot_folder, t)

        createFolder(self.screenshot_sub_folder)

        # weibo login

        # self.driver.get('https://passport.weibo.cn/signin/login')

        # time.sleep(20)

        # self.driver.find_element_by_xpath('//*[@id="loginName"]').clear()
        # self.driver.find_element_by_xpath('//*[@id="loginName"]').send_keys(username)
        # self.driver.find_element_by_xpath('//*[@id="loginPassword"]').clear()
        # time.sleep(1)
        # self.driver.find_element_by_xpath('//*[@id="loginPassword"]').send_keys(password)
        # time.sleep(2)

        # self.driver.find_element_by_xpath('//*[@id="loginAction"]').click()

        # time.sleep(20)

    def spider_closed(self, spider, reason):
        self.driver.service.process.send_signal(signal.SIGTERM)
        self.driver.quit()

    def process_request(self, request, spider):

        # Check if request requires to use phantomjs
        if request.meta.get('selenium') is None:
            return

        # Request required to use phantomjs
        if request.meta.get('selenium') == 0:

            phantom = webdriver.PhantomJS()

            tried = 0

            while True:

                try:

                    phantom.get(request.url)

                    phantom.get_screenshot_as_file("{}/{}.png".format(self.screenshot_sub_folder,
                                                       request.url.split('/')[-1]))

                    time.sleep(5)

                    pre = phantom.find_element_by_tag_name("pre").text

                    if pre:

                        body = pre

                    else:

                        body = phantom.page_source

                    phantom.quit()

                    return HtmlResponse(phantom.current_url, body=body, encoding='utf-8', request=request)

                except TimeoutException as ex:
                    print("Exception has been thrown. " + str(ex))

                    if tried == 5:
                        phantom.quit()
                        return
                    tried += 1

        # Desktop end request
        elif request.meta.get('selenium') == 1:

            user_id = request.meta.get('user_id')

            max_behot_time = request.meta.get('max_behot_time')

            try:

                self.driver.get(request.url)

                self.driver.get_screenshot_as_file("{}/{}.png".format(self.screenshot_sub_folder,
                                                                      request.url.split('/')[-2]))

                self.driver.refresh()

                time.sleep(5)

                js = 'return window.TAC.sign({}{})'.format(user_id, max_behot_time)

                signature = self.driver.execute_script(js)

                js = 'return ascp.getHoney()'

                ascp = self.driver.execute_script(js)

                data = {
                    'page_type': 1,
                    'user_id': user_id,
                    'max_behot_time': max_behot_time,
                    'count': 20,
                    'as': '',
                    'cp': '',
                    '_signature': '0'
                }

                data['_signature'] = signature

                data['as'] = ascp['as']
                data['cp'] = ascp['cp']

                url = 'https://www.toutiao.com/c/user/article/?' + urlencode(data)

                self.driver.execute_script(
                    "window.open('https://www.toutiao.com/c/user/98011335869/#mid=1599501878996996');")

                time.sleep(5)

                self.driver.get(url)

                body = self.driver.find_element_by_tag_name("pre").text

                return HtmlResponse(self.driver.current_url, body=body, encoding='utf-8', request=request)

            except TimeoutException as ex:
                print("Exception has been thrown. " + str(ex))

        # Scroll
        elif request.meta.get('selenium') == 2:

            self.driver.get(request.url)

            time.sleep(10)

            self.driver.refresh()

            indexPage = 0

            self.driver.get_screenshot_as_file("{}/{}.png".format(self.screenshot_sub_folder, indexPage))

            lastHeight = self.driver.execute_script("return document.body.scrollHeight")

            while True:

                try:

                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

                    n = random.randint(5, 15)

                    time.sleep(n)

                    self.driver.get_screenshot_as_file(
                        "{}/{}.png".format(self.screenshot_sub_folder, indexPage))

                    newHeight = self.driver.execute_script("return document.body.scrollHeight")

                    if lastHeight == newHeight:
                        break

                    lastHeight = newHeight

                    indexPage += 1

                except TimeoutException as ex:
                    print("Exception has been thrown. " + str(ex))

            body = self.driver.page_source

            return HtmlResponse(self.driver.current_url, body=body, encoding='utf-8', request=request)

        # Mobile end request
        elif request.meta.get('selenium') == 3:

            self.driver.get('https://m.toutiao.com/profile/98011335869/')

            time.sleep(5)

            self.driver.refresh()

            time.sleep(5)

            self.driver.get(request.url)

            body = self.driver.find_element_by_tag_name('pre').text

            self.driver.get_screenshot_as_file("{}/{}.png".format(self.screenshot_sub_folder,int(time.time())))

            return HtmlResponse(self.driver.current_url, body=body, encoding='utf-8', request=request)