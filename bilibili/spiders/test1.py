# -*- coding: utf-8 -*-
import scrapy


class Test1Spider(scrapy.Spider):
    name = 'test1'
    allowed_domains = ['www.freebuf.com']

    def start_requests(self):
        yield scrapy.Request(url='https://www.freebuf.com/news/193214.html', meta={'a': 1}, callback=self.parse, )
        yield scrapy.Request(url='https://www.freebuf.com/news/193214.html', meta={'a': 2}, callback=self.parse)

    def parse(self, response):
        print(f"链接：{response.meta.get('a')}")
