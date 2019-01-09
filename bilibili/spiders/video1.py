# -*- coding: utf-8 -*-
import scrapy
import json
import pymysql
import time
import logging

from bilibili.items import dynamicItem, staticItem
from scrapy.utils.project import get_project_settings


class VideoSpider(scrapy.Spider):
    name = 'video1'
    allowed_domains = ['api.bilibili.com']
    base_url = 'https://api.bilibili.com/x/article/archives?ids='
    code = 0

    def start_requests(self):
        # 获取设置中的mysql连接信息
        settings = get_project_settings()
        host = settings.get('MYSQL_HOST')
        database = settings.get('MYSQL_DATABASE')
        user = settings.get('MYSQL_USER')
        password = settings.get('MYSQL_PASSWORD')
        port = settings.get('MYSQL_PORT')

        # 创建mysql连接
        con = pymysql.connect(host=host, port=port, database=database, user=user, password=password)
        cursor = con.cursor()
        last = 0

        # 根据获取的aid号，构造url连接
        while 1:
            # 每次取10万条
            start = time.time()
            sql = f'SELECT aid FROM `video_static` where aid>{last} LIMIT 100000'
            rs = time.time()
            cursor.execute(sql)
            results = cursor.fetchall()
            if len(results) == 0:
                break
            last = results[-1][0]
            middle = time.time()
            logging.info(f'数据库查询用时：{middle - start}')

            # 每一百个aid号生成一条连接
            for i in range(0, len(results), 100):
                try:
                    s = ','.join([str(x[0]) for x in results[i:i + 100]])
                    yield scrapy.Request(url=self.base_url + s, callback=self.parse_json_dynamic)
                except IndexError:
                    s = ','.join([str(x[0]) for x in results[i:]])
                    yield scrapy.Request(url=self.base_url + s, callback=self.parse_json_dynamic)
                if i % 1000 == 0:
                    re = time.time()
                    if re - rs != 0:
                        print(f'\r每秒请求数为：{round(10/(re - rs), 2)}个', end='')
                    rs = time.time()
            end = time.time()
            logging.info(f'获取1K条链接共用时：{(end - start)//60}分{(end - start) % 60}秒')

        logging.info('----------开始获取当天最新视频信息----------')
        for i in range(last, last + 1000000, 100):
            s = ','.join([str(x) for x in range(i, i + 100)])
            yield scrapy.Request(url=self.base_url + s, callback=self.parse_json)
            if self.code == 2:
                break

    def parse_json_dynamic(self, response):
        try:
            page = json.loads(response.body)
        except Exception:
            # 如果json文件解析失败，重新爬取该页面
            return scrapy.Request(url=response.url, callback=self.parse_json)
        code = int(page['code'])
        if code == -404:
            self.code += 1
            return
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

    def parse_json(self, response):
        try:
            page = json.loads(response.body)
        except Exception:
            # 如果json文件解析失败，重新爬取该页面
            return scrapy.Request(url=response.url, callback=self.parse_json)
        code = int(page['code'])
        if code == -404:
            self.code += 1
            return
        for video in page['data'].values():
            item = staticItem()
            item['aid'] = video['stat']['aid']
            # 视频静态属性
            item['tid'] = video['tid']
            item['pic'] = video['pic']
            item['videos'] = video['videos']
            item['copyright'] = video['copyright']
            item['pubdate'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(video['pubdate']))
            item['duration'] = video['duration']
            item['title'] = video['title']
            item['mid'] = video['owner']['mid']
            # 视频动态属性
            item['view'] = video['stat']['view']
            item['danmaku'] = video['stat']['danmaku']
            item['reply'] = video['stat']['reply']
            item['favorite'] = video['stat']['favorite']
            item['coin'] = video['stat']['coin']
            item['share'] = video['stat']['share']
            item['like'] = video['stat']['like']
            yield item
