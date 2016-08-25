# -*- coding: utf-8 -*-
# Python version: Python 3.4.3

from .movie_related_info import get_movieBasicInfo_parseHtml
from .utils import update_new_fields, get_current_time
from .global_variables import *
from .download_mtime import extend_movieIds_by_traverse_movieId


def func(x):
    sq = x**2
    print(sq)


def task_func(*args, **kwargs):
    pass


def task_update_movie_fields_info(movieId):
    """扩充电影的字段信息"""
    new_info = get_movieBasicInfo_parseHtml(movieId)
    update_new_fields(coll_movieBasicInfo, new_info)
    coll_movieBasicInfo.update({'_id': movieId}, {'$set': {'is_processed': True}})  # 标记为已处理
    last_update_time = get_current_time()
    coll_movieBasicInfo.update({'_id': movieId}, {'$set': {'last_update_time': last_update_time}})  # 记录更新时间

##res = task_update_movie_fields_info(107491)


def task_extend_movieIds_by_traverse_movieId(movieId):
    """遍历电影ID，扩充电影条目数"""
    extend_movieIds_by_traverse_movieId(movieId)

