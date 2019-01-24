import os
import time
import pymysql

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# 该启动脚本需放在项目根目录的同级目录，否则无法正确识别模块
# 必须先加载项目settings配置
# project需要改为你的工程名字（即settings.py所在的目录名字）
if __name__ == '__main__':
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'bilibili.settings')

    # 从settings文件中读取配置信息
    settings = get_project_settings()
    # 获取当前日期作为表名
    dynamic_table = 'video_dynamic_' + time.strftime("%y%m%d", time.localtime())
    log_file = 'log' + time.strftime('%y%m%d', time.localtime()) + '.log'
    # 设置settings中的插入表名
    settings.set(name='DYNAMIC_TABLE_NAME', value=dynamic_table)
    # settings.set(name='LOG_FILE', value=log_file)
    # mysql连接信息
    host = settings.get('MYSQL_HOST')
    database = settings.get('MYSQL_DATABASE')
    user = settings.get('MYSQL_USER')
    password = settings.get('MYSQL_PASSWORD')
    port = settings.get('MYSQL_PORT')
    # 创建mysql连接
    db = pymysql.connect(host=host, port=port, user=user, password=password, database=database)

    # 按照爬取日期创建数据表
    cursor = db.cursor()
    sql = 'SET FOREIGN_KEY_CHECKS=0;'
    cursor.execute(sql)
    sql = 'DROP TABLE IF EXISTS `' + dynamic_table + '`;'
    cursor.execute(sql)
    sql = "CREATE TABLE `" + dynamic_table + \
          """`(`aid` int(11) NOT NULL,
                `view` int(11) DEFAULT NULL,
                `danmaku` int(11) DEFAULT NULL,
                `reply` int(11) DEFAULT NULL,
                `favorite` int(11) DEFAULT NULL,
                `coin` int(11) DEFAULT NULL,
                `share` int(11) DEFAULT NULL,
                `like` int(11) DEFAULT NULL,
                PRIMARY KEY (`aid`)
              ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
          """
    cursor.execute(sql)

    process = CrawlerProcess(settings)
    # 指定多个spider
    process.crawl("video1")
    # 执行所有 spider
    # for spider_name in process.spider_loader.list():
    #     process.crawl(spider_name)
    process.start()
