# -*- coding: utf-8 -*-
# Python version: Python 3.4.3

from .utils import *
from .global_variables import *
import json

# --------------------------------------

def get_movieCategory():
    """获得电影分类信息"""
    url = 'http://api.m.mtime.cn/Movie/GetSearchItem.api'
    resp = get_response_body(url, return_type='json', delay=True)
    data = resp.get('data')
    for category in data:
        doc = {}
        doc['_id'] = category
        doc['category_info'] = data.get(category)
        try:
            db.movieCategory.insert(doc)
        except:
            pass

##res = get_movieCategory()

# --------------------------------------

# API请求获得电影信息

def get_AreasGenretypesYears(coll_movieCategory):
    """获得category的areas, genreTypes, years列表信息"""
    areas = [doc.get('subName') for doc in coll_movieCategory.find_one({'_id': 'area'})['category_info']]
    genreTypes = [doc.get('subName') for doc in coll_movieCategory.find_one({'_id': 'genreTypes'})['category_info']]
    years = [doc.get('smallName') for doc in coll_movieCategory.find_one({'_id': 'years'})['category_info']]

    return areas, genreTypes, years

##res = get_AreasGenretypesYears(coll_movieCategory)


def get_movieBasicInfo_searchMovieApi(areas, genreTypes, years, coll_movieBasicInfo, doc_perpage=10, fail_times=5):
    """通过API的方式获得电影信息"""

    url = u'http://api.m.mtime.cn/Movie/SearchMovie.api?areas={}&genreTypes={}&years={}&sortType=0&sortMethod=1'.format(areas, genreTypes, years)
    try:
        resp = get_response_body(url, return_type='json', delay=True)
    except:
        return

    data = resp.get('data')
    totalCount = data.get('totalCount')

    max_page, _ = divmod(totalCount, doc_perpage)
    previous_movieId_list = []

    page_num = 0
    repeat_pages = 0
    while True:
        page_num += 1
        if page_num > max_page:
            return

        sleep_time = random.random()
        sleep(sleep_time)
        url = u'http://api.m.mtime.cn/Movie/SearchMovie.api?areas={}&genreTypes={}&years={}&sortType=0&sortMethod=1&pageIndex={}'.format(areas, genreTypes, years, page_num)
        try:
            resp = get_response_body(url, return_type='json', delay=True)
        except:
            continue
        data = resp.get('data')
        movieModelList = data.get('movieModelList')
        if movieModelList:
            movieId_list = []

            for dic in movieModelList:
                movieId = dic.get('movieId')
                movieId_list.append(movieId)
                if coll_movieBasicInfo.find_one({'_id': movieId}):
                    print('Movie <{}> has been existed!\n'.format(movieId))
                    continue
                dic['_id'] = movieId
                try:
                    coll_movieBasicInfo.insert(dic)
                    print('>>> [success!] New movie <{}> !\n'.format(movieId))
                except:
                    pass
            if movieId_list == previous_movieId_list:
                repeat_pages += 1
                if repeat_pages > fail_times:
                    return
                print('> repeat_pages: {}/{} !\n'.format(repeat_pages, fail_times))

            previous_movieId_list = deepcopy(movieId_list)


def run_movieBasicInfo_searchMovieApi():
    """通过类型组合，API搜索得到电影信息"""
    areas, genreTypes, years = get_AreasGenretypesYears(coll_movieCategory)
    for district in areas:
        for genre in genreTypes:
            for ye in years:
                print(u'==== areas = {}, genreTypes = {}, years = {} ====\n'.format(district, genre, ye))
                fail_times = random.randint(3, 5)
                get_movieBasicInfo_searchMovieApi(district, genre, ye, coll_movieBasicInfo, fail_times=fail_times)

##res = run_movieBasicInfo_searchMovieApi()


# --------------------------------------

# 影评信息

def get_HotShortComments(movieId):
    """获得电影的微影评"""
    if coll_movieBasicInfo.find_one({'_id': movieId, 'hotShortComments': {'$exists': True}}):
        print('> [existed!] HotShortComments have been existed for movie -> [{}]\n'.format(movieId))
        return

    url = 'http://api.m.mtime.cn/Showtime/HotMovieComments.api?movieId={}'.format(movieId)
    resp = get_response_body(url, return_type='json', delay=True)
    if resp is None:  # 没有返回数据
        coll_movieBasicInfo.update({'_id': movieId}, {'$set': {'hotShortComments': ''}})
        return

    data = resp.get('data')
    totalCount = data.get('totalCount')
    comments_list = []  # 微评论列表

    next_page = 0
    while True:
        next_page += 1
        sleep_time = random.random()
        sleep(sleep_time)
        url = 'http://api.m.mtime.cn/Showtime/HotMovieComments.api?movieId={}&pageIndex={}'.format(movieId, next_page)
        resp = get_response_body(url, return_type='json', delay=True)
        data = resp.get('data')
        comments = data.get('cts')
        if comments:
            comments_list.extend(comments)
        else:  # 没有返回新的影评信息
            doc = {'totalCount': totalCount, 'comments_list': comments_list}
            coll_movieBasicInfo.update({'_id': movieId}, {'$set': {'hotShortComments': doc}})
            print('>>> [new!] hotShortComments -> {}\n'.format(movieId))
            return

##res = get_HotShortComments('207872', coll_shortHotMovieComments)


def get_HotLongComments(movieId):
    """获得电影的热门长影评.

    完整内容: http://api.m.mtime.cn/Review/Detail.api?reviewId=294574
    """
    if coll_movieBasicInfo.find_one({'_id': movieId, 'hotLongComments': {'$exists': True}}):
        print('> [existed!] HotLongComments have been existed for movie -> [{}]\n'.format(movieId))
        return
##    url = 'http://api.m.mtime.cn/Review/Detail.api?reviewId=294574'

    url = 'http://api.m.mtime.cn/Movie/HotLongComments.api?movieId={}'.format(movieId)
    resp = get_response_body(url, return_type='json', delay=True)
    totalCount = resp.get('totalCount')
    comments_list = {}  # 长评论列表

    next_page = 0
    while True:
        next_page += 1
        sleep_time = random.random()
        sleep(sleep_time)
        url = 'http://api.m.mtime.cn/Movie/HotLongComments.api?movieId={}&pageIndex={}'.format(movieId, next_page)
        resp = get_response_body(url, return_type='json', delay=True)
        comments = resp.get('comments')
        if comments:
            for comment in comments:
                reviewId = comment.get('id')
                detail_review = get_review_detail(reviewId)
                comments_list[str(reviewId)] = detail_review  # 转化为字符串，否则报错

        else:  # 没有新的评论了
            doc = {'totalCount': totalCount, 'comments_list': comments_list}
            coll_movieBasicInfo.update({'_id': movieId}, {'$set': {'hotLongComments': doc}})
            print('>>> [new!] hotLongComments -> {}\n'.format(movieId))
            return

##res = get_HotLongComments(17926, coll_hotLongComments)

def get_review_detail(reviewId):
    """获得完整长评论"""
    url = 'http://api.m.mtime.cn/Review/Detail.api?reviewId={}'.format(reviewId)

    try:
        detail_review = get_response_body(url, return_type='json', delay=True)
        return detail_review
    except:
        print(url)

# ---------------------------------------

# 通过解析网页，获得电影主要基本信息

def get_movieBasicInfo_parseHtml(movieId):
    url = 'http://movie.mtime.com/{}/'.format(movieId)
    resp_sel = get_response_body(url, delay=True)
    movie_info = {}

    # 具体信息
    base_info_1 = get_base_info_1(resp_sel)  # 电影中文名，电影英文名，年份，电影时长，电影类别，发行日期，发行地点
    movie_info.update(base_info_1)

    base_info_2 = get_base_info_2(resp_sel) # 导演，编剧，国家地区，发行公司等. 注意: 字段名不是一成不变的!
    movie_info.update(base_info_2)

    main_actor = get_main_actor(resp_sel)  # 主演
    movie_info.update(main_actor)

    plots = get_plots(movieId)  # 剧情
    movie_info.update(plots)

    rating_info = get_movie_ratingInfo(movieId)  # 电影评价信息, e.g.票房，评分等
    movie_info.update(rating_info)

    behind_the_scene = get_behind_the_scene(movieId)  # 幕后揭秘, e.g.拍摄花絮，幕后制作等
    movie_info.update(behind_the_scene)

    fullcredits = get_fullcredits(movieId)  # 电影全部演员表和角色,actor;character等
    movie_info.update(fullcredits)

    # movie id
    movie_info['_id'] = movieId
    movie_info['movieId'] = movieId

    return movie_info

##res = get_movieBasicInfo_parseHtml(89824)
##res = get_movieBasicInfo_parseHtml(125283)


def get_base_info_1(resp_sel):
    """电影中文名，电影英文名，年份，电影时长，电影类别，发行日期，发行地点"""
    info = {'movie_name_cn': '',
            'movie_name_en': '',
            'movie_releaseYear': '',
            'movie_runtime': '',
            'movie_genre': '',
            'movie_initialReleaseDate': '',
            'movie_releasePlace': ''
            }

    movie_name_cn = ''.join(resp_sel.select('//div[@class="db_head"]/div[@class="clearfix"]/h1/text()').extract())  # 电影中文名
    movie_name_en = ''.join(resp_sel.select('//div[@class="db_head"]/div[@class="clearfix"]/p[@class="db_enname"]/text()').extract())  # 电影英文名
    movie_releaseYear = ''.join(resp_sel.select('//div[@class="db_head"]/div[@class="clearfix"]/p[@class="db_year"]/a/text()').extract())  # 年份
    movie_runtime = ''.join(resp_sel.select('//div[@class="db_head"]/div[@class="otherbox __r_c_"]/span[@property="v:runtime"]/text()').extract())  # 电影时长
    movie_genre = resp_sel.select('//div[@class="db_head"]/div[@class="otherbox __r_c_"]//a[@property="v:genre"]//text()').extract()  # 电影类别
    movie_initialReleaseDate = ''.join(resp_sel.select('//div[@class="db_head"]/div[@class="otherbox __r_c_"]/a[@property="v:initialReleaseDate"]/@content').extract())  # 电影初始发行时期
    movie_releasePlace = resp_sel.select('//div[@class="db_head"]/div[@class="otherbox __r_c_"]/text()').extract()
    movie_releasePlace = '' if movie_releasePlace == [] else movie_releasePlace[-1]

    info = {'movie_name_cn': movie_name_cn,
            'movie_name_en': movie_name_en,
            'movie_releaseYear': movie_releaseYear,
            'movie_runtime': movie_runtime,
            'movie_genre': movie_genre,
            'movie_initialReleaseDate': movie_initialReleaseDate,
            'movie_releasePlace': movie_releasePlace
            }

    return info


def get_base_info_2(resp_sel):
    """导演，编剧，国家地区，发行公司等.
    注意: 字段名不是一成不变的!
    """
    info = {}

    sel_list = resp_sel.select('//div[@class="clearfix pt15"]/dl[@class="info_l"]//dd[@pan="M14_Movie_Overview_BaseInfo"]')
    for sel in sel_list:
        field =  ''.join(sel.select('.//strong/text()').re('\w+'))
        values = ';'.join(sel.select('.//a/text()|.//span/text()').extract())
        info[field] = values

    return info

##resp_sel = get_response_body('http://movie.mtime.com/218662/')
##resp_sel = get_response_body('http://movie.mtime.com/82264/')
##resp_sel = get_response_body('http://movie.mtime.com/80225/')
##res = get_base_info_2(resp_sel)


def get_main_actor(resp_sel):
    """主演"""
    info = {'main_actor': ''}

    sel_list = resp_sel.select('//dl[@class="main_actor"]')
    actors = []
    for sel in sel_list:
        personId = ''.join(sel.select('.//dd/a[@class="__r_c_"]/@href').re('\d+'))
        img = ''.join(sel.select('.//dd/a[@class="__r_c_"]/img/@src').extract())
        name, nameEn = extract_actor_name(sel)
        person_doc = {'_id': int(personId) if personId else '',  # 原有字段类型为Int32
                      'id': int(personId) if personId else '',
                      'image': img,
                      'name': name,
                      'nameEn': nameEn
                      }
        actors.append(person_doc)

    info['main_actor'] = actors

    return info

def extract_actor_name(sel):
    """提取演员中英文名字"""
    name = sel.select('.//dd/p[@class="__r_c_"]//a//text()').extract()
    if name == []:  # 没有提取到
        return ('', '')

    elif len(name) == 2:  # 有两个名字，此处代码不一定正确，有待验证
        if has_chinease(name[0]):  # 第一个名字含有中文
            return name
        return name[::-1]

    elif len(name) == 1:  # 只有一个名字
        if has_chinease(name[0]):
            return (name[0], '')
        return ('', name[0])


def get_plots(movieId):
    """剧情"""
    url = 'http://movie.mtime.com/{}/plots.html'.format(movieId)
    resp_sel = get_response_body(url)
##    plots = ''.join(resp_sel.xpath('//div[@id="paragraphRegion"]/div[@class="plots_out"]//div[@class="plots_box"]//text()').re('\S+'))
    plots = ''.join(resp_sel.select('//div[@id="paragraphRegion"]/div[@class="plots_out"]//div[@class="plots_box"]//text()').re('\S+'))

    return {'plots': plots}

##res = get_plots(89824)


def get_movie_ratingInfo(movieId):
    """获得电影评价信息"""
    info = {'movieRating': '',  # 评价信息
            'boxOffice': '',  # 票房信息
            'releaseType': ''
            }

    url = 'http://service.library.mtime.com/Movie.api?'\
    'Ajax_CallBack=true&Ajax_CallBackType=Mtime.Library.Services&Ajax_CallBackMethod=GetMovieOverviewRating'\
    '&Ajax_CrossDomain=1&Ajax_RequestUrl=http://movie.mtime.com/{}/&Ajax_CallBackArgument0={}'.format(movieId, movieId)
    text = get_response_body(url, return_type='html', delay=True)
    text = re.search('{.+}', text).group(0)
    json_text = json.loads(text)
    data = json_text.get('value')
    if data is None:
        return info

    movieRating = data.get('movieRating')
    info['movieRating'] = movieRating
    boxOffice = data.get('boxOffice')
    info['boxOffice'] = boxOffice
    releaseType = data.get('releaseType')
    info['releaseType'] = releaseType

    return info

##res = get_movie_ratingInfo(89824)
##res = get_movie_ratingInfo(218662)



def get_behind_the_scene(movieId):
    """幕后揭秘, e.g.拍摄花絮，幕后制作等"""

    info = {'behind_the_scene': ''}

    url = 'http://movie.mtime.com/{}/behind_the_scene.html'.format(movieId)
    resp_sel = get_response_body(url)

##    behind_the_scene = ''.join(resp_sel.xpath('//div[@class="details_cont"]//text()').re('\S+'))  # 新版本的scrapy支持
    # 旧版本的scrapy
    if resp_sel:
        behind_the_scene = ''.join(resp_sel.select('//div[@class="details_cont"]//text()').re('\S+'))
        info['behind_the_scene'] = behind_the_scene

    return info

##res = get_behind_the_scene(89824)
##res = get_behind_the_scene(10054)


def get_fullcredits(movieId):
    """电影全部演员表和角色,actor;character等"""
    info = {'movieCredits': ''}

    url = 'http://api.m.mtime.cn/Movie/MovieCreditsWithTypes.api?movieId={}'.format(movieId)
    resp = get_response_body(url, return_type='json')
    if resp:
        movieCredits = resp.get('types', '')
        info['movieCredits'] = movieCredits
        return info
    return info

##res = get_fullcredits(10024)

##run_get_movieBasicInfo_parseHtml()

##res = get_movieBasicInfo_parseHtml(114241)
##res = get_movieBasicInfo_parseHtml(89824)
##res = get_movieBasicInfo_parseHtml(125283)




