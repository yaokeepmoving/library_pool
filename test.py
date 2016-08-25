# -*- coding: utf-8 -*-
# Python version: Python 3.4.3

from presentaion_corpus.src.global_variables import *

def generate_task_id_list(start_index=0, end_index=1000000):
    for _id in range(start_index, end_index):
        yield {'_id': _id}




#
