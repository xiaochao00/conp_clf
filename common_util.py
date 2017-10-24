#!/usr/bin/python
#coding=utf8
"""
# Author: andy
# Created Time : 2017-04-20 19:55:37

# File Name: util.py
# Description:
# 某些常用函数

"""

import sys
import math


def cosine_txt(vec1, vec2, len1=0, len2=0):
    '计算文字向量的cosine'
    #input:
    #vec1: {term1:val1, term2:val2 ...}
    if len(vec1) == 0 or len(vec2) == 0:
        return 0.0
    multi = 0.0
    l1 = 0.0
    l2 = 0.0
    for t in vec1:
        if t in vec2:
            multi += vec1[t] * vec2[t]
        if len1 == 0:
            l1 += vec1[t] * vec1[t]
    if len2 == 0:
        for t in vec2:
            l2 += vec2[t] * vec2[t]
    if len1 == 0:
        len1 = math.sqrt(l1)
    if len2 == 0:
        len2 = math.sqrt(l2)
    #print "multi:%f, len1:%f, len2:%f" % (multi, len1, len2)
    cosine = multi / (len1 * len2)
    return cosine

def eu_distance(vec1, vec2):
    '计算两个向量的欧氏距离'
    eu_sum = 0.0
    for t in vec1:
        if t in vec2:
            eu_sum += (vec1[t] - vec2[t]) * (vec1[t] - vec2[t])
        else:
            eu_sum += vec1[t] * vec1[t]
    for t in vec2:
        if not(t in vec1):
            eu_sum += vec2[t] * vec2[t]
    eu_sum = math.sqrt(eu_sum)
    return eu_sum


def vec_len(vec):
    '计算向量的模, vec是dict'
    m = 0.0
    for k in vec:
        m += vec[k] * vec[k]
    return math.sqrt(m)

def cosine(vec1, vec2, len1=0, len2=0):
    '计算数字向量的cos, 输入向量已按feaid升序排列'
    i = 0
    j = 0
    sum = 0
    flag1 = 0
    flag2 = 0
    if len1 == 0:
        flag1 = 1
    if len2 == 0:
        flag2 = 1
    nend1 = 1
    nend2 = 1
    #while nend1 or nend2:
    while i < len(vec1) and j < len(vec2):
        if vec1[i][0] == vec2[j][0]:
            sum += vec1[i][1] * vec2[j][1]
            if flag1 == 1:
                len1 += vec1[i][1] * vec1[i][1]
            if flag2 == 1:
                len2 += vec2[j][1] * vec2[j][1]
            i += 1
            j += 1
        elif vec1[i][0] < vec2[j][0]:
            if flag1 == 1:
                len1 += vec1[i][1] * vec1[i][1]
            i += 1
        else:
            if flag2 == 1:
                len2 += vec2[j][1] * vec2[j][1]
            j += 1
    if i < len(vec1):
        while i < len(vec1):
            if flag1 == 1:
                len1 += vec1[i][1] * vec1[i][1]
            i += 1
    if j < len(vec2):
        while j < len(vec2):
            if flag2 == 1:
                len2 += vec2[j][1] * vec2[j][1]
            j += 1

    if flag1 == 1:
        len1 = math.sqrt(len1)
    if flag2 == 1:
        len2 = math.sqrt(len2)
    return sum/(len1 * len2)

