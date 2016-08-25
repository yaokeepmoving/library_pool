# -*- coding: utf-8 -*-
# Python version: Python 3.4.3

import mtime.src.task as task_module
from mtime.src.utils import get_task_list_from_redis
from mtime.src.global_variables import *
import gevent
from gevent.pool import Pool
from gevent import monkey
import sys


monkey.patch_all()

##task_list = [219628]
##for ele in task_list:
##    task_update_movie_fields_info(ele)

class Task(object):

    def __init__(self, task_name):
        self.task_name = task_name
        self.__task_func = getattr(task_module, task_name)  # 用同名字符串调用函数

    def run(self, task_pool, pool_num=10):
        print('>>> start run task: {} ...\n'.format(self.task_name))
        spider_pool = Pool(pool_num)
        for task_list in task_pool:
            spider_pool.map(self.__task_func, task_list)
        print('\nJob Done!\n')

# --------------------------------------

# demo
##if __name__ == '__main__':
##    print('python {} --task_name --job_num=10'.format(sys.argv[0]))
##    task_name = sys.argv[1]
##    pool_num = int(sys.argv[2])
##    task_pool = [[2, 2, 3], [2, 2, 3]]
##    task = Task(task_name)
##    task.run(task_pool, pool_num)



# 补充字段信息
##if __name__ == '__main__':
##    monkey.patch_all()
##    print('python {} --job_num=10'.format(sys.argv[0]))
##    if len(sys.argv) < 2:
##        raise IndexError('The command line parameter number is less than 2!')
##
##    spider_pool = Pool(int(sys.argv[1]))
##    task_pool = get_task_list_from_redis(redis, 'task_update_movie_fields_info')
##    for task_list in task_pool:
##        spider_pool.map(task_update_movie_fields_info, task_list)
##
##    print('Done!')


if __name__ == '__main__':
    print('python {} --task_name --job_num=10'.format(sys.argv[0]))
    task_name = sys.argv[1]
    pool_num = int(sys.argv[2])
    task_pool = get_task_list_from_redis(client_redis, task_name)
    task = Task(task_name)
    task.run(task_pool, pool_num)

# --------------------------------------


# person -> movie -> person -> ...
##if __name__ == '__main__':
##
##    print('python {} --job_num=10\n'.format(sys.argv[0]))
##
##    if len(sys.argv) == 2:
##        spider_pool = Pool(int(sys.argv[1]))
##        person2movie2person()
##
####    spider_pool = Pool(10)
####    person2movie2person()

# 遍历directors表
##if __name__ == '__main__':
##    print('python {} --job_num=10'.format(sys.argv[0]))
##    total_num = 0
##    if len(sys.argv) == 2:
##        spider_pool = Pool(int(sys.argv[1]))
##        while True:
##            need_processed_persons = coll_peopleIds.find({'is_processed': {'$exists': False}}).limit(100)
##            person_num = need_processed_persons.count(with_limit_and_skip=True)
##            if person_num > 0:
##                total_num += person_num
##                print('==> [process: {}] ...\n'.format(total_num))
##                spider_pool.map(person2movie, need_processed_persons)  # 协程
##                print('==> [finished: {}]\n'.format(total_num))
##            else:
##                break
##        print('Done!')
##
##    client_mongo.close()