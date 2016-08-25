# -*- coding: utf-8 -*-
# Python version: Python 3.4.3


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.action_chains import ActionChains

from .global_variables import *

from .utils import (save_response_body, get_response_body)

# ----------------------------------------


# 下载导演ID
def get_directors():
    js = 'var q=document.documentElement.scrollTop=10000'
    opts = webdriver.ChromeOptions()
    opts.binary_location = r"D:\Program Files\Chrome\chrome.exe"
    driver = webdriver.Chrome(chrome_options = opts)
    wait = ui.WebDriverWait(driver,10)

##    url = 'http://movie.mtime.com/people/search/section/#'
    url = 'http://movie.mtime.com/people/search/section/#pageIndex=679&constellation=0&bloodType=100&filmographyId=2'
    driver.get(url)

##    bt_director = driver.find_elements_by_css_selector('#filmographyId > li:nth-child(2) > a:nth-child(1)')[0]
##    bt_director.click() # 点击导演按钮
    sleep(random.random() * 30)
    page_cnt = 0
    while True:
        page_cnt += 1
        print('page_cnt = {}\n'.format(page_cnt))
        driver = extract_director_id(driver) # 保存每页的导演ID
        has_next_page = driver.find_elements_by_id('key_nextpage')  # 是否有下一页
        if not has_next_page:
            break

        driver.execute_script(js)  # 滚动条到底部
        sleep(random.random() * 10)
        bt_next_page = driver.find_element_by_id('key_nextpage')
        try:
            bt_next_page.click()
        except:
            print('>>> Error! please input check code...\n')
            sleep(30)  # 等待20秒输入验证码
            bt_next_page = driver.find_element_by_id('key_nextpage')
            bt_next_page.click()
        sleep(random.random() * 10)


def extract_director_id(driver):

    try:
        director_list = driver.find_elements_by_xpath('//h3[@class="normal mt6"]/a')
        director_list = [ele.get_attribute('href') for ele in director_list]
        director_list = [int(re.search('\d+', ele).group(0)) for ele in director_list]
        print('> {} directors\n'.format(len(director_list)))
        for _id in director_list:
            if not coll_directors.find_one({'_id': _id}):
                coll_directors.insert({'_id': _id, 'id': _id})
                print('>>> [new doc!] coll_directors -> {}\n'.format(_id))
    except:
        print('> [Error!] extract_director_id(driver)\n')
        sleep(10)

    return driver

##res = get_directors()

# --------------------------------------------


def extend_movieIds_by_traverse_movieId(movie_id):
    resp = get_new_movieId(movie_id)
    if resp:
        data = resp.get('types')
        if data:
            try:
                dump2movieCreditsWithTypes(data, movie_id)  # 保存信息 -> 电影的相关工作人员(按照类别分)
                update_people(data)  # 更新影人信息
            except:
                pass

    print('=== extend_movieIds_by_traverse_movieId(movie_id) -> {} ===\n'.format(movie_id))


def get_new_movieId(movie_id):
    if coll_movieBasicInfo.find_one({'_id': movie_id}):
        return None

    url = 'http://movie.mtime.com/{}/'.format(movie_id)

    try:
        resp = get_response_body(url, return_type='html')
        if u'很抱歉，你要访问的页面不存在' in resp:
            return None

        url = 'http://api.m.mtime.cn/Movie/MovieCreditsWithTypes.api?movieId={}'.format(movie_id)
        resp = get_response_body(url, return_type='json')
        data = resp.get('types')
        if data:
            coll_movieBasicInfo.insert({'_id': movie_id, 'id': movie_id})  # 更新movieIds表
            print('> [new doc!] coll_movieBasicInfo -> {}\n'.format(movie_id))
            save_response_body(url, resp, response_type='json')  # 保存请求返回结果
            return resp
    except:
        traceback.print_exc()
        print('>>> [Error!] get_new_movieId(movie_id) -> {}\n'.format(url))

    return None


# ------------------------------------------


def movie2person(movie_doc):
    """由movieId获得电影的参与人员信息.
    MovieCreditsWithTypes: 电影的相关工作人员(按照类别分)
    """
    movieId = movie_doc['_id']
    url = 'http://api.m.mtime.cn/Movie/MovieCreditsWithTypes.api?movieId={}'.format(movieId)

    try:
        resp = get_url_json(url)
        data = resp.get('types')
        if data:
            dump2movieCreditsWithTypes(data, movieId)  # 保存信息 -> 电影的相关工作人员(按照类别分)
            update_people(data)  # 更新影人信息
            coll_movieIds.update({'_id': movieId}, {'$set': {'is_processed': True}})  # 标记成已处理

    except:
        print('>>> [fail!] movie2person(movieId) -> {}\n'.format(movieId))


def dump2movieCreditsWithTypes(data, movieId):
    """保存信息 -> 电影的相关工作人员(按照类别分)"""

    if not coll_movieBasicInfo.find_one({'_id': movieId}):
        coll_movieBasicInfo.insert({'_id': movieId, 'id': movieId, 'movieCredits': data})
        print('>>> [new doc!] coll_movieBasicInfo -> {}\n'.format(movieId))
    else:  # 记录存在，但演员表信息不存在
        if coll_movieBasicInfo.find_one({'_id': movieId,'movieCredits': {'$exists': False}}):  # 如果字段'movieCredits'不存在，则添加演员表字段信息
            coll_movieBasicInfo.update({'_id': movieId}, {'$set': {'movieCredits': data}})
            print('> [new fields (movieCredits)!] coll_movieBasicInfo -> {}\n'.format(movieId))

def update_people(data):
    """更新影人表信息"""
    for movieCredits in data:
        persons = movieCredits.get('persons')
        for person_doc in persons:
            person_id = person_doc.get('id')
            update_peopleIds(person_id)  # 更新电影人物ID表
            if not coll_peopleBasicInfo.find_one({'_id': person_id}):  # 如果表中条目已存在，会出现信息丢失!
                doc = {'_id': person_id,
                       'id': person_doc.get('id'),
                       'name': person_doc.get('name'),
                       'nameEn': person_doc.get('nameEn'),
                       'image': person_doc.get('image')
                       }
                coll_peopleBasicInfo.insert(doc)
                print('> [new!] coll_peopleBasicInfo -> {}\n'.format(person_id))


def update_peopleIds(person_id):
    """# 更新电影人物ID表"""
    if not coll_peopleIds.find_one({'_id': person_id}):
        coll_peopleIds.insert({'_id': person_id, 'id': person_id})
        print('> [new!] coll_peopleIds -> {}\n'.format(person_id))

##res = movie2person(32686)

# ------------------------------------------

def person2movie(person_doc):
    """由personId获得演员作品信息"""
    personId = person_doc['_id']
    page_num = 1
    filmographies = []

    while True:
        url = 'http://api.m.mtime.cn/Person/Movie.api?personId={}&pageIndex={}&orderId=2'.format(personId, page_num)
        try:
            if coll_response_body.find_one({'_id': url}):
                data = coll_response_body.find_one({'_id': url}).get('response_body')
            else:
                data = get_url_json(url)
            if data:
                save_response_body(url, data) # 保存响应结果
                filmographies.extend(data) # 部分作品
                update_movies(data)  # 更新电影信息
            else: # data = []，已经没有新页面
                dump2peopleFilmographies(personId, filmographies) # 保存信息 -> # 演员作品年表
                coll_peopleIds.update({'_id': personId}, {'$set': {'is_processed': True}})  # 标记成已处理
                break
        except:
            traceback.print_exc()
            print('>>> [fail!] person2movie(person_doc) -> {}\n'.format(personId))

        page_num += 1  # 有的演员比较高产


def dump2peopleFilmographies(personId, filmographies):
    """ # 保存信息 -> # 演员作品年表"""
    if not coll_peopleFilmographies.find_one({'_id': personId}):
        doc = {'_id': personId,
               'id': personId,
               'filmographies': filmographies
               }
        coll_peopleFilmographies.insert(doc)
        print('>>> [new doc!] coll_peopleFilmographies -> <{}>\n'.format(personId))


def update_movies(data):
    """ # 更新电影信息"""
    for movie_doc in data:
        movieId = movie_doc.get('id')
        update_movieIds(movieId)  # 更新电影IDs表

        if not coll_movieBasicInfo.find_one({'_id': movieId}):  # 如果表中条目已存在，会出现信息丢失!
            doc = {'_id': movieId,
                   'id': movieId,
                   'image': movie_doc.get('image'),
                   'name': movie_doc.get('name'),
                   'year': movie_doc.get('year'),
                   'rating': movie_doc.get('rating'),
                   'releaseDate': movie_doc.get('releaseDate'),
                   'releaseCountry': movie_doc.get('releaseCountry'),
                   }
            coll_movieBasicInfo.insert(doc)
            print('>>> [new doc!] coll_movieBasicInfo -> <{}> !\n'.format(movieId))


def update_movieIds(movieId):
    """ # 更新电影IDs表"""
    if not coll_movieIds.find_one({'_id': movieId}):
        coll_movieIds.insert({'_id': movieId, 'id': movieId})
        print('>>> [new doc!] coll_movieIds -> [{}] !\n'.format(movieId))

# --------------------------------------------


def person2movie2person():
    """自我拓展： person -> movies -> people -> ..."""
    stop_person2movie = False
    stop_movie2person = False
    while True:
        need_processed_persons = coll_peopleIds.find({'is_processed': {'$exists': False}}).limit(100)  # 如果字段'is_processed'不存在，则返回一个需要处理的personId
        if need_processed_persons.count(with_limit_and_skip=True) > 0:
            print('============ person2movie ===========\n')
            spider_pool.map(person2movie,need_processed_persons)
        else:
            stop_person2movie = True

        need_processed_movies = coll_movieIds.find({'is_processed': {'$exists': False}}).limit(100)  # 如果字段'is_processed'不存在，则返回一个需要处理的personId
        if need_processed_movies.count(with_limit_and_skip=True) > 0:
            print('============ movie2person ===========\n')
            spider_pool.map(movie2person,need_processed_movies)
        else:
            stop_movie2person = True

        if stop_person2movie and stop_movie2person:
            print('job done!')
            break

# ----------------------------------------------

def get_comments():
    """获得长短影评"""
    no_short_comments = False
    no_long_comments = False

    while True:
        short_comments = coll_movieBasicInfo.find_one({'hotShortComments': {'$exists': False}})
        if short_comments:
            movieId = short_comments['_id']
            movie_related_info.get_HotShortComments(movieId, coll_movieBasicInfo)
        else:
            no_short_comments = True

        long_comments = coll_movieBasicInfo.find_one({'hotLongComments': {'$exists': False}})
        if long_comments:
            movieId = long_comments['_id']
            movie_related_info.get_HotLongComments(movieId, coll_movieBasicInfo)
        else:
            no_long_comments = True

        if no_short_comments and no_long_comments:
            print('[Done!] get_comments\n')
            break

##get_comments()

##person2movie(892754, coll_movieIds, coll_movieBasicInfo, coll_peopleIds, coll_peopleFilmographies)
##person2movie(2210553, coll_movieIds, coll_movieBasicInfo, coll_peopleIds, coll_peopleFilmographies)

# --------------------------------------




