# -*- coding: utf-8 -*-
# Python version: Python 3.4.3

"""爬虫相关的类和函数"""

class BaseSpider(object):
    """爬虫基类"""
    def __init__(self, spider_name, homepage):
        self.__spider_name = spider_name
        self.homepage = homepage

