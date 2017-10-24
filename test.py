#!/usr/bin/python
#coding=utf8
"""
# Author: andy
# Created Time : 2017-10-16 15:34:05

# File Name: test.py
# Description:

"""
import sys
from topicSim import topicSim

if __name__ == '__main__':
    data_path = './topicSim/data'
    if topicSim.initial(data_path):
        print('initial error')
        exit(1)
    test_file = './topicSim/data/test'
    txt_list = []
    tfile = open(test_file)
    for line in tfile.readlines():
        line = line.decode('utf-8')
        line = line.rstrip('\n')
        tlist = line.split('\t')
        title = tlist[1]
        content = tlist[1]
        txt_list.append({'title':title, 'content':content})
    tfile.close()
    res_list = topicSim.topic_sim(txt_list, sim_thresh=0.03)
    for i in range(len(res_list)):
        res_str = ''
        for res_data in res_list[i]['list']:
            res_str = '%s|%s %.4f' % (res_str, res_data['name'], res_data['sim'])
        res_str = res_str.lstrip('|')
        print (res_str + '\t' + txt_list[i]['title']).encode('utf-8')

