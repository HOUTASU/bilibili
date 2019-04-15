# -*- coding: utf-8 -*-
import scrapy
import json
import pymysql
from scrapy.utils.project import get_project_settings
from bilibili.items import upItem


class UPSpider(scrapy.Spider):
    name = 'up'
    allowed_domains = ['api.bilibili.com']
    start_urls = ['http://api.bilibili.com/']
    settings = get_project_settings()
    fans_url = 'https://api.bilibili.com/x/relation/stat?vmid={}&jsonp=jsonp'
    archive_url = 'https://api.bilibili.com/x/space/upstat?mid={}&jsonp=jsonp'
    custom_settings = {
        'ITEM_PIPELINES': {
            'bilibili.pipelines.MongoPipeline': 300,
        },
        'DOWNLOAD_DELAY': 0.2
    }

    def start_requests(self):
        mysql_config = self.settings.get('MYSQL_CONFIG')
        mysql_config['database'] = 'biliweb'
        my_conn = pymysql.connect(**mysql_config)

        sql = "select mid from  bdvs_up;"
        cursor = my_conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        for mid in results:
            yield scrapy.Request(url=self.fans_url.format(mid[0]), meta={'mid': mid[0]}, callback=self.parse_fans)

    def parse_fans(self, response):
        meta = response.meta
        try:
            page = json.loads(response.body)
        except Exception:
            # 如果json文件解析失败，重新爬取该页面
            return scrapy.Request(url=response.url, meta=meta, callback=self.parse_fans)

        meta['fans'] = page['data']['follower']
        meta['follow'] = page['data']['following']
        yield scrapy.Request(url=self.archive_url.format(meta['mid']), meta=meta, callback=self.parse_archive)

    def parse_archive(self, response):
        meta = response.meta
        try:
            page = json.loads(response.body)
        except Exception:
            # 如果json文件解析失败，重新爬取该页面
            return scrapy.Request(url=response.url, meta=meta, callback=self.parse_fans)
        item = upItem()
        item['mid'] = meta['mid']
        item['fans'] = meta['fans']
        item['follow'] = meta['follow']
        item['archive'] = page['data']['archive']['view']
        item['article'] = page['data']['article']['view']
        yield item
