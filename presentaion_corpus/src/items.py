# -*- coding: utf-8 -*-
# Python version: Python 3.4.3

from scrapy import Field, Item


class ChinaEntrepreneursForumItem(Item):
    title = Field()  # 文章标题
    text = Field()  # 文章正文
    date_time = Field()  # 日期时间
    author = Field()  # 作者
    hits = Field()  # 点击量

    page_url = Field()  # 文章地址
    category = Field()  # 所属分类
    source = Field()  # 来源
    source_homepage = Field()  # 来源主页

    download_time = Field()  # 下载日期

