# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import time
import pymysql
import pymongo
from pymysql.err import IntegrityError
from bilibili.items import dynamicItem, upItem


class MysqlPipeline(object):
    # 批量插入，每100条写成一条sql语句,减少数据库访问次数

    def __init__(self, mysql_config, dynamic_table):
        mysql_config['charset'] = 'utf8'
        self.mysql_config = mysql_config
        self.dynamic_table = dynamic_table
        self.item_list_1 = []
        self.item_list_2 = []

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mysql_config=crawler.settings.get('MYSQL_CONFIG'),
            dynamic_table=crawler.settings.get('DYNAMIC_TABLE_NAME'),
        )

    def open_spider(self, spider):
        self.dbpool = pymysql.connect(**self.mysql_config)
        self.cursor = self.dbpool.cursor()

    def close_spider(self, spider):
        self.dbpool.close()

    def process_item(self, item, spider):
        # 用全局列表保存数据，每满100条时执行一次插入
        if type(item) is dynamicItem:
            self._insert_dynamic(item)
        else:
            self._insert_static(item)
            self._insert_dynamic(item)
        return item

    def _insert_dynamic(self, item):
        if len(self.item_list_1) < 100:
            self.item_list_1.append((item['aid'], item['view'], item['danmaku'], item['reply'], item['favorite'],
                                     item['coin'], item['share'], item['like']))
        else:
            try:
                sql = f'insert into {self.dynamic_table} values ' + str(self.item_list_1)[1:-1] + ';'
                self.cursor.execute(sql)
                self.dbpool.commit()
                self.item_list_1.clear()
            # 异常处理，如果遇到重复插入，则重新对这一批次的每条数据进行插入
            # 对于重复的行直接忽略
            except IntegrityError:
                for x in self.item_list_1:
                    try:
                        sql = f'insert into {self.dynamic_table} values {x};'
                        self.cursor.execute(sql)
                        self.dbpool.commit()
                    except IntegrityError:
                        pass
                self.item_list_1.clear()

    def _insert_static(self, item):
        if len(self.item_list_2) < 100:
            self.item_list_2.append((item['aid'], item['tid'], item['videos'], item['pubdate'], item['mid'],
                                     item['copyright'], item['duration'], item['title'], item['pic']))
        else:
            try:
                sql = f'insert into video_static values {str(self.item_list_2)[1:-1]};'
                self.cursor.execute(sql)
                self.dbpool.commit()
                self.item_list_2.clear()
            # 异常处理，如果遇到重复插入，则重新对这一批次的每条数据进行插入
            # 对于重复的行直接忽略
            except Exception:
                for x in self.item_list_2:
                    try:
                        sql = f'insert into video_static values {x};'
                        self.cursor.execute(sql)
                        self.dbpool.commit()
                    except Exception:
                        pass
                self.item_list_2.clear()


# class VideoPipeline(object):
#     # 批量插入，每100条写成一条sql语句,减少数据库访问次数
#
#     def __init__(self, mysql_config, dynamic_table):
#         mysql_config['charset'] = 'utf-8'
#         mysql_config['database'] = 'biliweb'
#         mysql_config['cursorclass'] = pymysql.cursors.DictCursor
#         self.mysql_config = mysql_config
#         self.dynamic_table = dynamic_table
#         self.item_list_1 = []
#         self.item_list_2 = []
#
#     @classmethod
#     def from_crawler(cls, crawler):
#         return cls(
#             mysql_config=crawler.settings.get('MYSQL_CONFIG'),
#             dynamic_table=crawler.settings.get('DYNAMIC_TABLE_NAME'),
#         )
#
#     def open_spider(self, spider):
#         self.dbpool = pymysql.connect(**self.mysql_config)
#         self.cursor = self.dbpool.cursor
#
#     def close_spider(self, spider):
#         self.dbpool.close()
#
#     def process_item(self, item, spider):
#         # 用全局列表保存数据，每满100条时执行一次插入
#         sql = f"select * from bdvs_video where aid={item['aid']}"
#         self.cursor.execute(sql)
#         res = self.cursor.fetchall()
#         if len(res) == 0:
#             self._insert_dynamic(item)
#         else:
#             pass
#         return item
#
#     def _insert_dynamic(self, item):
#         s = ','.join(['%s' * 8])
#         try:
#             sql = f"insert into {self.dynamic_table} values ({s});"
#             self.cursor.execute(sql, (
#                 item['aid'], item['view'], item['danmaku'], item['reply'], item['favorite'], item['coin'],
#                 item['share'], item['like']))
#             self.dbpool.commit()
#         except IntegrityError:
#             pass
#
#     def _update_dynamic(self, data, item):
#         sql = "ALTER TABLE `video_data` ADD COLUMN `state` TINYINT(2) NOT NULL DEFAULT '0' COMMENT '0为添加1为编辑' "
#         sql = f"update bdvs_video set view = {data['view']} where aid = {data['aid']};"
#         self.cursor.excute(sql)
#         self.dbpool.commit()


# mongo数据库连接及插入
class MongoPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    # 从setting文件中获取mongo连接及数据库名称
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    # 连接mongo数据库
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    # item插入集合中，集合名在item类中定义
    def process_item(self, item, spider):
        if type(item) is dynamicItem:
            self.insert_video(item)
        if type(item) is upItem:
            self.insert_up(item)
        return item

    def insert_video(self, item):
        _item = dict(item)
        video = self.db['video_data'].find_one({'_id': str(item['aid'])})
        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        if video is None:
            _item['trace_time'] = now
            self.db['video_data'].save({'_id': str(item['aid'])})
            video = self.db['video_data'].find_one({'_id': str(item['aid'])})
        _item['trace_time'] = now
        video[str(len(video))] = _item
        self.db['video_data'].update_one({'_id': video['_id']}, {'$set': video})

    def insert_up(self, item):
        _item = dict(item)
        up = self.db['up_data'].find_one({'_id': str(item['mid'])})
        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        if up is None:
            _item['trace_time'] = now
            self.db['up_data'].save({'_id': str(item['mid'])})
            up = self.db['up_data'].find_one({'_id': str(item['mid'])})
        _item['trace_time'] = now
        up[str(len(up))] = _item
        self.db['up_data'].update_one({'_id': up['_id']}, {'$set': up})

    # 关闭mongo连接
    def close_spider(self, spider):
        self.client.close()
