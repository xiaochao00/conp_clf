#!/usr/bin/python
#coding=utf8
"""
# Author: andy
# Created Time : 2017-10-15 14:31:48

# File Name: check_res.py
# Description:
检查分类结果 
"""
import sys

def check_res(res_file):
    rfile = open(res_file)
    for line in rfile.readlines():
        line = line.decode('utf-8')
        line = line.rstrip('\n')
        tlist = line.split('\t')
        tag = tlist[0]
        if tlist[1] == '':
            print(line.encode('utf-8'))
            continue
        pre_list = tlist[1].split('|')
        '''
        if len(pre_list) != 1:
            print(line.encode('utf-8'))
            continue
        '''
        for pre_str in pre_list:
            pre_data = pre_str.split(' ')
            if pre_data[0] == tag:
                break
        else:
            print(line.encode('utf-8'))
            continue
    rfile.close()


if __name__ == '__main__':
    res_file = 'test.all.res'
    check_res(res_file)

