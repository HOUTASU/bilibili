# encoding: utf-8

"""
@author: sw
@contact: 237298062@qq.com
@software: PyCharm
@time: 2019/4/22 11:26
"""

# -*- coding: utf-8 -*-
import requests
import json
import pymysql
import time

MYSQL_CONFIG = {
    'host': '119.27.176.229',
    'port': 10012,
    'database': 'bili',
    'user': 'root',
    'password': 'cuit051072sW+'
}

online_url = 'https://api.bilibili.com/x/web-interface/online'
r = requests.get(online_url)
data = json.loads(r.text)
play_online = data['data']['play_online']
web_online = data['data']['web_online']

mc = pymysql.Connect(**MYSQL_CONFIG)
cursor = mc.cursor()
sql = 'insert into online (web_online, play_online, trace_time)value({},{},sysdate())'.format(web_online, play_online)
cursor.execute(sql)
mc.commit()
mc.close()


