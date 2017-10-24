#!/usr/bin/python
#coding=utf8
"""
# Author: andy
# Created Time : 2017-10-16 10:18:36

# File Name: topicSim.py
# Description:
# 用概念分类的方法对文本分类，这是个1vo的方法

"""

import sys
import json
import match_concept

worker = None
event_conp = {}
def initial(data_path):
    # 初始化
    # input: data_path:数据路径
    # output: 1:error, 0:success
    model_path = data_path
    conp_file = '/conp_list'
    vocabulary = '/vocabulary'
    #jieba_dict = data_path + '/jieba_user.dict.org.fil'
    parameter = {'base_path':data_path, 'model_path':model_path, 'vocabulary':vocabulary, 'conp_file':conp_file}
    input_jstr = json.dumps(parameter)
    global worker
    try:
        worker = match_concept.Worker(input_jstr)
    except Exception, ex:
        print Exception, ex
        return 1

    event_conp_file = data_path + '/event_conp'
    ecfile = open(event_conp_file)
    for line in ecfile.readlines():
        line = line.decode('utf-8')
        line = line.rstrip('\n')
        tlist = line.split('\t')
        event = tlist[0]
        conp = tlist[1]
        event_conp[event] = conp
    ecfile.close()
    return 0


def topic_sim(txt_list, sim_thresh=0.03):
    # 计算输入文本和conp的相关度
    # input:
    # txt_list: [{'title':title, 'content':content}, ]
    # sim_thresh: 相关度阈值, 如果相关度小于阈值则不返回该conp的结果
    # output: [{'list':[{'name':conp_string, 'sim':sim_value_float}, ]}, ]
    # output: None:有错误
    global worker
    raw_data = []
    for txt_data in txt_list:
        raw_data.append({'data':{'title':txt_data['title'], 'content':txt_data['content']}, 'config':{'t':sim_thresh}})
    input_jstr = json.dumps(raw_data)
    res_jstr = worker.process(input_jstr)
    res_data = json.loads(res_jstr)
    return res_data['message']


def event2conp(event):
    # 返回事件对应的conp
    # input: event:事件名称
    # output: conp:conp名称, '':没有对应的conp
    if event is None:
        return ''
    global event_conp
    conp = event_conp.get(event, '')
    return conp


if __name__ == '__main__':
    # test topic_sim
    data_path = './data'
    if initial(data_path):
        print('initial error')
        sys.exit(1)
    test_file = './data/test'
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
    res_list = topic_sim(txt_list, sim_thresh=0.03)
    for i in range(len(res_list)):
        res_str = ''
        for res_data in res_list[i]['list']:
            res_str = '%s|%s %.4f' % (res_str, res_data['name'], res_data['sim'])
        res_str = res_str.lstrip('|')
        print (res_str + '\t' + txt_list[i]['title']).encode('utf-8')

    # test event2conp
    print event2conp(u'无法偿还政府债务')

