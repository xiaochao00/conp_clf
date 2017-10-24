#!/usr/bin/python
#coding=utf8
"""
# Author: andy
# Created Time : 2017-10-12 16:36:24

# File Name: make_neg_corpus.py
# Description:
# 提取负例训练语料

"""
import sys
import jieba

def load_event_rel(rel_file):
    # 读取事件相关词, 并加入分词词典
    word_dict = {}
    name_list = []
    rfile = open(rel_file)
    for line in rfile.readlines():
        line = line.decode('utf-8')
        line = line.rstrip('\n')
        tlist = line.split('\t')
        # 事件类型名称
        name_list.append(tlist[0])
        # 事件相关词
        for w in tlist[1:]:
            if w not in word_dict:
                word_dict[w] = {}
                jieba.add_word(w, 100)
            word_dict[w][tlist[0]] = 1
    rfile.close()
    name_set = set(name_list)
    return word_dict, name_set


def make_neg_corpus(corpus_file, word_dict, name_set, output_file):
    # 生成事件负例语料, 即不包含该事件相关词的语料
    # intput:
    # corpus_file:原始语料
    # word_dict:事件相关词dict
    # name_set:事件名称set
    # output_file:负例语料输出文件
    ofile = open(output_file, 'w')
    cfile = open(corpus_file)
    while 1:
        lines = cfile.readlines()
        if not lines:
            break
        for line in lines:
            line = line.decode('utf-8')
            line = line.rstrip('\n')
            tlist = line.split('\t')
            title = tlist[2]
            content = tlist[3]
            cur_events = set()
            term_list = jieba.cut(title + '#&#' + content)
            for term in term_list:
                if term in word_dict:
                    for name in word_dict[term]:
                        cur_events.add(name)
            if not cur_events:
                continue
            diff_names = name_set - cur_events
            ofile.write(('%s\t%s\t%s\n' % ('|'.join(diff_names), title, content)).encode('utf-8'))
    cfile.close()
    ofile.close()


if __name__ == '__main__':
    rel_file = '../data/event_rel'
    word_dict, name_set = load_event_rel(rel_file)
    corpus_file = '../data/org_news.2'
    #output_file = '../data/neg_corpus.2'
    output_file = '../data/neg_corpus.3'
    make_neg_corpus(corpus_file, word_dict, name_set, output_file)



