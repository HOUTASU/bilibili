# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
from pymysql.err import IntegrityError
from bilibili.items import staticItem, dynamicItem


# # mongo数据库连接及插入
# class MongoPipeline(object):
#     def __init__(self, mongo_uri, mongo_db):
#         self.mongo_uri = mongo_uri
#         self.mongo_db = mongo_db
#
#     # 从setting文件中获取mongo连接及数据库名称
#     @classmethod
#     def from_crawler(cls, crawler):
#         return cls(
#             mongo_uri=crawler.settings.get('MONGO_URI'),
#             mongo_db=crawler.settings.get('MONGO_DB')
#         )
#
#     # 连接mongo数据库
#     def open_spider(self, spider):
#         self.client = pymongo.MongoClient(self.mongo_uri)
#         self.db = self.client[self.mongo_db]
#
#     # item插入集合中，集合名在item类中定义
#     def process_item(self, item, spider):
#         self.db[item.collection].insert(dict(item))
#         return item
#
#     # 关闭mongo连接
#     def close_spider(self, spider):
#         self.client.close()


class MysqlPipeline(object):
    # 批量插入，每100条写成一条sql语句,减少数据库访问次数

    def __init__(self, host, database, user, password, port, dynamic_table):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.dynamic_table = dynamic_table
        self.item_list_1 = []
        self.item_list_2 = []

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MYSQL_HOST'),
            database=crawler.settings.get('MYSQL_DATABASE'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            port=crawler.settings.get('MYSQL_PORT'),
            dynamic_table=crawler.settings.get('DYNAMIC_TABLE_NAME'),
        )

    def open_spider(self, spider):
        self.dbpool = pymysql.connect(host=self.host, user=self.user, password=self.password,
                                      database=self.database, charset='utf8', port=self.port)
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
                sql = f'insert into video_static values ' + str(self.item_list_2)[1:-1] + ';'
                self.cursor.execute(sql)
                self.dbpool.commit()
                self.item_list_2.clear()
            # 异常处理，如果遇到重复插入，则重新对这一批次的每条数据进行插入
            # 对于重复的行直接忽略
            except IntegrityError:
                for x in self.item_list_2:
                    try:
                        sql = f'insert into video_static values {x};'
                        self.cursor.execute(sql)
                        self.dbpool.commit()
                    except IntegrityError:
                        pass
                self.item_list_2.clear()
