# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import logging
import redis
from random import choice


class BilibiliSpiderMiddleware(object):
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

    # def process_spider_output(self, response, result, spider):
    #     # Called with the results returned from the Spider, after
    #     # it has processed the response.
    #
    #     # Must return an iterable of Request, dict or Item objects.
    #     for i in result:
    #         yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    # def process_start_requests(self, start_requests, spider):
    #     # Called with the start requests of the spider, and works
    #     # similarly to the process_spider_output() method, except
    #     # that it doesn’t have a response associated.
    #
    #     # Must return only requests (not items).
    #     for r in start_requests:
    #         yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class UserAgentMiddleware(object):
    def __init__(self):
        self.user_agent_list = [
            'MSIE (MSIE 6.0; X11; Linux; i686) Opera 7.23',
            'Opera/9.20 (Macintosh; Intel Mac OS X; U; en)',
            'Opera/9.0 (Macintosh; PPC Mac OS X; U; en)',
            'iTunes/9.0.3 (Macintosh; U; Intel Mac OS X 10_6_2; en-ca)',
            'Mozilla/4.76 [en_jp] (X11; U; SunOS 5.8 sun4u)',
            'iTunes/4.2 (Macintosh; U; PPC Mac OS X 10.2)',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:5.0) Gecko/20100101 Firefox/5.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:9.0) Gecko/20100101 Firefox/9.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:16.0) Gecko/20120813 Firefox/16.0',
            'Mozilla/4.77 [en] (X11; I; IRIX;64 6.5 IP30)',
            'Mozilla/4.8 [en] (X11; U; SunOS; 5.7 sun4u)'
        ]

    def process_request(self, request, spider):
        request.headers['USER_AGENT'] = choice(self.user_agent_list)


class ErrorCodeMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self, redisDB):
        self.redisDB = redisDB

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        redis_host = settings.get('REDIS_HOST')
        redis_port = settings.get('REDIS_PORT')
        redis_pwd = settings.get('REDIS_PASSWORD')
        return cls(
            redisDB=redis.Redis(host=redis_host, port=redis_port, )
        )

    def process_response(self, request, response, spider):
        if response.status != 200:
            proxy = request.meta.get("proxy")
            if proxy:
                self.redisDB.zincrby('proxies', proxy.split('/')[-1].encode('utf-8'), -1)
        return response


class ProxyMiddleware(object):
    def __init__(self, redisDB):
        self.logger = logging.getLogger(__name__)
        self.redisDB = redisDB

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        redis_host = settings.get('REDIS_HOST')
        redis_port = settings.get('REDIS_PORT')
        redis_pwd = settings.get('REDIS_PASSWORD')
        return cls(
            redisDB=redis.Redis(host=redis_host, port=redis_port, )
        )

    def get_random_proxy(self):
        result = self.redisDB.zrangebyscore('proxies', 10, 10)
        if len(result):
            return choice(result).decode('utf-8')
        else:
            result = self.redisDB.zrevrange('proxies', 5, 10)
            if len(result):
                return choice(result).decode('utf-8')
            else:
                raise PoolEmptyError

    def process_request(self, request, spider):
        proxy = self.get_random_proxy()
        if proxy:
            uri = 'http://{proxy}'.format(proxy=proxy)
            self.logger.debug('使用代理 ' + proxy)
            request.meta['proxy'] = uri


class PoolEmptyError(Exception):

    def __init__(self):
        Exception.__init__(self)

    def __str__(self):
        return repr('代理池已经枯竭')
