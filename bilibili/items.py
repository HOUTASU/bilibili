# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class dynamicItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    aid = Field()
    # tid = Field()
    # videos = Field()
    # pubdate = Field()
    # mid = Field()
    # copyright = Field()
    # duration = Field()
    # title = Field()
    # pic = Field()
    view = Field()
    danmaku = Field()
    reply = Field()
    favorite = Field()
    coin = Field()
    share = Field()
    like = Field()


class staticItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    aid = Field()
    tid = Field()
    videos = Field()
    pubdate = Field()
    mid = Field()
    copyright = Field()
    duration = Field()
    title = Field()
    pic = Field()
    view = Field()
    danmaku = Field()
    reply = Field()
    favorite = Field()
    coin = Field()
    share = Field()
    like = Field()
