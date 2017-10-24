#!/usr/bin/python
#coding=utf8
"""
# Author: andy
# Created Time : 2017-10-15 19:52:32

# File Name: news_segment.py
# Description:
对新闻分词 
"""

import sys
import common_segment


if __name__ == '__main__':
    usr_dict = '../data/jieba_user.dict.org.fil'
    common_segment.seg_initial(usr_dict)
    news_file = '../data/
