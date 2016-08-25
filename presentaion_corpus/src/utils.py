# -*- coding: utf-8 -*-
# Python version: Python 3.4.3

import requests
from time import sleep
from scrapy.http import HtmlResponse
from scrapy.selector import HtmlXPathSelector
import random
from .global_variables import *
import re
import time
import json


# ---------------------------------------

def create_collection(client, coll_name):
    pass


def get_task_list_from_redis(redis_client, key, chunk_size=100):
    """从redis产生任务片段"""
    while True:
        task_chunk =[]
        for i in range(chunk_size):
            job = client_redis.rpop(key)
            if job:
                dic = json.loads(job.decode('utf-8'))
                _id = dic.get('_id')
                task_chunk.append(_id)
            else:
                print('Done!')
                break
        yield task_chunk


def put_task_into_redis(redis_client, key, task_list):
    """将任务队列push到redis中"""
    for dic in task_list:
        doc = {'_id': dic.get('_id')}
        redis_client.rpush(key, json.dumps(doc))
    print('[Done!] task list pushed into redis key: {}\n'.format(key))


def get_current_time(time_format='%Y-%m-%d %H:%M:%S'):
    """获得系统当前时间"""
    return time.strftime(time_format, time.localtime())


def compare_doc_id(coll_1, coll_2):
    """在coll_1中，但不在coll_2中"""
    keys_1 = set(coll_1.distinct('_id'))
    keys_2 = set(coll_2.distinct('_id'))

    return keys_1.difference(keys_2)


def update_new_fields(coll, new_doc):
    """向原有document添加新的key:value"""

    _id = new_doc.get('_id')
    old_doc = coll.find_one({'_id': _id})
    new_keys = get_new_keys(new_doc, old_doc)
    if new_keys:
        update_doc = {k: new_doc.get(k) for k in new_keys if k}  # 需要更新的key:value对
##        print(update_doc)
        coll.update({'_id': _id}, {'$set': update_doc})
        print('>>> [New fields!] collection_name: < {coll_name} > || new_fields: < {new_fields} > || _id: < {doc_id} >\n'.format(coll_name=coll.full_name, new_fields=new_keys, doc_id=_id))
    else:
        print('>>> [No new fields!] collection_name: < {coll_name} > || new_fields: < {new_fields} > || _id: < {doc_id} >\n'.format(coll_name=coll.full_name, new_fields=new_keys, doc_id=_id))


def get_new_keys(new_doc, old_doc):
    """获得新的keys"""
    new_keys = list(new_doc.keys())
    old_keys = list(old_doc.keys())
    return set(new_keys) - set(old_keys)


def has_chinease(st):
    """判断字符串里是否含有中文"""
    zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
    has_zh = zhPattern.findall(st)
    if has_zh:
        return True
    return False


def combine_collection(coll_master, coll_slave):
    """将coll_slave的doc合并到coll_master中"""
    for doc in coll_slave.find({}):
        _id = doc.get('_id')
        if not coll_master.find_one({'_id': _id}):
            coll_master.insert(doc)
            print('> from {} to {}\n -> {}'.format(coll_slave, coll_master, _id))


##combine_collection(coll_peopleIds, coll_directors)


def save_response_body(url, response_body, response_type=''):
    """保存请求结果，避免多次请求"""
    if not coll_response_body.find_one({'_id': url}):
        coll_response_body.insert({'_id': url, 'url': url, 'response_body': response_body, 'response_type': response_type})
        print('> [new!] save_response_body(url, response_body, response_type='') -> {}\n'.format(url))


def get_url_json(url,try_times = 2):
    """请求API，返回json格式的数据"""
    data = None
    while try_times:
        try:
            sleep(random.random() * 10)
            data = requests.get(url, headers=headers).json()
            break
        except:
            try_times -= 1
            print ('> [request error!] [get_url_json(url,try_times = 5)] get <{}>\n'.format(url))
    return data

##res = get_url_json('http://api.m.mtime.cn/Person/Movie.api?personId=893017&pageIndex=1&orderId=2')


def split_list(max_index, start_index=0, chunk_size=500):
    """切分列表"""
    for i in range(start_index, max_index, chunk_size):
        j = i + chunk_size
        if j < max_index:
            yield range(i, i+chunk_size)
        else:
            yield range(i, max_index+1)

##res = split_list(100, 7, 7)
##for ele in res:
##    print(list(ele))


def get_url_hxs(url,is_json=False):
    """使用代理IP请求"""
    proxies = [{'https':'220.248.230.217:3128'},{'https':'119.18.234.60:80'},{'https':'218.90.174.167:3128'},{'https':'1.82.216.135:80'},{'https':'120.25.163.76:3128'}]
    ran_index = random.randint(0,5)
    hxs = None
    try_count = 10
    while try_count > 0:
        if is_json:
            try:
                user_agent = ['"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0"']
                headers={'User-Agent':user_agent}
                json_content = requests.get(url,headers=headers,timeout=50,proxies = proxies[ran_index]).json()
                break
            except Exception as e:
                json_content = []
        else:
            try:
                user_agent = ['"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0"']
                headers={'User-Agent':user_agent}
                body = requests.get(url,headers=headers,timeout=50,proxies = proxies[ran_index]).content
                response = HtmlResponse(url=url, body=body)
                hxs = HtmlXPathSelector(response)
                break
            except Exception as e:
                hxs = None
        try_count -= 1
    return json_content if is_json else hxs


def get_response_body(url, return_type='selector', timeout=10, try_times=2, delay=True):
    """返回响应的body.
    return_type='selector'/'json/html'
    """
    proxies = [{'https':'220.248.230.217:3128'},{'https':'119.18.234.60:80'},{'https':'218.90.174.167:3128'},{'https':'1.82.216.135:80'},{'https':'120.25.163.76:3128'}]
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'}
    ran_index = random.randint(0, len(proxies) - 1)

    fail_times = 0

    if return_type == 'selector':  # 解析html，返回response Selector
        while True:
            if delay:  # 设置时间间隔
                sleep(random.random() * 10)
            try:
                html = requests.get(url, headers=headers, timeout=timeout, proxies=proxies[ran_index]).content
                resp = HtmlResponse(url, body=html)
                return HtmlXPathSelector(resp)

            except:
                fail_times += 1
                if fail_times > try_times:
                    return None
                pass

    elif return_type == 'json':  # 请求API, 返回json格式
        while True:
            if delay:  # 设置时间间隔
                sleep(random.random() * 10)
            try:
                resp = requests.get(url, headers=headers, timeout=timeout, proxies=proxies[ran_index]).json()
                return resp

            except:
                fail_times += 1
                if fail_times > try_times:
                    return None
                pass

    elif return_type == 'html':  # 返回html
        while True:
            if delay:  # 设置时间间隔
                sleep(random.random() * 10)

            try:
                resp = requests.get(url, headers=headers, timeout=timeout, proxies=proxies[ran_index]).content
                return resp.decode('utf-8')  # response返回的是bytes，需要转换成string

            except:
                fail_times += 1
                if fail_times > try_times:
                    return None
                pass


