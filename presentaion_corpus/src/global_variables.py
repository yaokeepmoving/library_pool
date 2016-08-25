# -*- coding: utf-8 -*-
# Python version: Python 3.4.3

import redis
from pymongo import MongoClient

# -------------------------------------------

##headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'}

##headers = { 'Host': 'movie.mtime.com',
##            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0',
##            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
##            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
##            'Accept-Encoding': 'gzip, deflate',
##            'Connection': 'keep-alive'}
##

#

websites = [{'_id': 'http://www.cefco.cn/',
             'website': '中国企业家论坛',
             'homepage': 'http://www.cefco.cn/'
             },
            {'_id': 'http://business.sohu.com/sohuentrepreneurs/',
             'website': '搜狐企业家论坛',
             'homepage': 'http://business.sohu.com/sohuentrepreneurs/'
             },

            {'_id': 'http://www.wysls.com/c/YanJiangGao/',
             'website': '大学生演讲网',
             'homepage': 'http://www.wysls.com/c/YanJiangGao/'
             },
            {'_id': 'http://www.zgxzw.com/xiaozhang/list.asp?p_id=48',
             'website': '中国校长网_校长频道_校长论坛',
             'homepage': 'http://www.zgxzw.com/xiaozhang/list.asp?p_id=48'
             },

            {'_id': 'http://finance.sina.com.cn/money/bank/pbcsf/',
             'website': '新浪财经论坛',
             'homepage': 'http://finance.sina.com.cn/money/bank/pbcsf/'
             },

            {'_id': 'http://bbs.chinacourt.org/',
             'website': '法治论坛',
             'homepage': 'http://bbs.chinacourt.org/'
             },
            {'_id': 'http://bbs.tianya.cn/list-law-1.shtml',
             'website': '天涯论坛_法制论坛',
             'homepage': 'http://bbs.tianya.cn/list-law-1.shtml'
             },
            {'_id': 'http://bbs1.people.com.cn/board/9.html',
             'website': '人民网_强国社区_法治论坛',
             'homepage': 'http://bbs1.people.com.cn/board/9.html'
             },

            {'_id': 'http://www.zfgzbg.com/index.asp',
             'website': '中国城市政府工作报告网',
             'homepage': 'http://www.zfgzbg.com/index.asp'
             },
            {'_id': 'http://www.chinareform.org.cn/open/view/',
             'website': '中国改革论坛网_对外开放_中国视野',
             'homepage': 'http://www.chinareform.org.cn/open/view/'
             },

            ]

# database client
##client_redis = redis.Redis('192.168.86.62', port=6379, db=7)
client_redis = redis.Redis('192.168.86.155', port=6379, db=10)

client_mongo = MongoClient('192.168.86.108', 27017)

# collections
db = client_mongo.presentation_corpus
coll_spider_websites = db.spider_websites
