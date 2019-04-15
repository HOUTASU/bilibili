import os
import time
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

if __name__ == '__main__':
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'bilibili.settings')
    # 从settings文件中读取配置信息
    settings = get_project_settings()

    process = CrawlerProcess(settings)
    # log_file = 'log' + time.strftime('%y%m%d', time.localtime()) + 'tracer.log'
    # settings.set(name='LOG_FILE', value=log_file)
    # 指定多个spider
    process.crawl("tracer")
    process.crawl('up')
    # 执行所有 spider
    # for spider_name in process.spider_loader.list():
    #     process.crawl(spider_name)
    process.start()
