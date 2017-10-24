#!/usr/bin/python
#coding=utf8
"""
# Author: andy
# Created Time : 2017-10-12 17:50:43

# File Name: make_vocabulary.py
# Description:
# 做训练用的基础词表

"""
import sys
import re
import jieba
import common_segment

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("need input_file & seg_output_file & tfdf_output_file")
        exit(0)
    usr_dict = '../data/jieba_user.dict.org.fil'
    jieba.load_userdict(usr_dict)

    # 把事件相关词加入分词词典
    rfile = open('../data/event_rel')
    word_dict = {}
    for line in rfile.readlines():
        line = line.decode('utf-8')
        line = line.rstrip('\n')
        tlist = line.split('\t')
        # 事件相关词
        for w in tlist[1:]:
            if w not in word_dict:
                word_dict[w] = {}
                jieba.add_word(w, 100)
    rfile.close()

    p_hanzi = re.compile(u'[\u3400-\u9fa5]')
    p_eng = re.compile('[a-zA-Z]')

    tf_dict = {}
    df_dict = {}
    ifile = open(sys.argv[1])
    oseg_file = open(sys.argv[2], 'w')
    otfdf_file = open(sys.argv[3], 'w')
    for line in ifile.readlines():
        line = line.decode('utf-8')
        line = line.rstrip('\n')
        tlist = line.split('\t')
        title = tlist[2]
        content = tlist[3]
        terms = common_segment.segment(title + '#&#' + content)
        oseg_file.write((' '.join(terms) + '\n').encode('utf-8'))

        tmp_dict = {}
        for term in terms:
            if len(term) == 1:
                continue
            if p_hanzi.search(term) is None and p_eng.match(term) is None:
                #print(term.encode('utf-8'))
                continue
            tf_dict[term] = tf_dict.setdefault(term, 0) + 1
            tmp_dict[term] = 1
        for term in tmp_dict:
            df_dict[term] = df_dict.setdefault(term, 0) + 1
    ifile.close()
    oseg_file.close()
    for term in tf_dict:
        otfdf_file.write(("%s\t%d\t%d\n" % (term, tf_dict[term], df_dict.get(term, 0))).encode('utf-8'))
    otfdf_file.close()

