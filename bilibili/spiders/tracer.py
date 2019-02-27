# -*- coding: utf-8 -*-
import scrapy
import json
import pymysql
from scrapy.utils.project import get_project_settings
from bilibili.items import dynamicItem


class TracerSpider(scrapy.Spider):
    name = 'tracer'
    allowed_domains = ['api.bilibili.com']
    start_urls = ['http://api.bilibili.com/']
    settings = get_project_settings()
    base_url = 'https://api.bilibili.com/x/article/archives?ids='

    def start_requests(self):
        mysql_config = self.settings.get('MYSQL_CONFIG')
        mysql_config['database'] = 'biliweb'
        my_conn = pymysql.connect(**mysql_config)

        sql = "select aid from  'bdvs_video';"
        cursor = my_conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        for i in range(0, len(results), 100):
            try:
                s = ','.join([str(x[0]) for x in results[i:i + 100]])
                yield scrapy.Request(url=self.base_url + s, callback=self.parse_json_dynamic)
            except IndexError:
                s = ','.join([str(x[0]) for x in results[i:]])
                yield scrapy.Request(url=self.base_url + s, callback=self.parse_json_dynamic)

    def parse_json_dynamic(self, response):
        try:
            page = json.loads(response.body)
        except Exception:
            # 如果json文件解析失败，重新爬取该页面
            return scrapy.Request(url=response.url, callback=self.parse_json_dynamic)
        for video in page['data'].values():
            item = dynamicItem()
            item['aid'] = video['stat']['aid']
            # 视频动态属性
            item['view'] = video['stat']['view']
            item['danmaku'] = video['stat']['danmaku']
            item['reply'] = video['stat']['reply']
            item['favorite'] = video['stat']['favorite']
            item['coin'] = video['stat']['coin']
            item['share'] = video['stat']['share']
            item['like'] = video['stat']['like']
            yield item
