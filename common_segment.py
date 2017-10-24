#!/usr/bin/python
#coding=utf-8
import re
import sys

import jieba

import common_bin_util
'''
from common_adaptor_dao import CommDao
'''
num_suffix = {u"亿":1,
u"亿元":1,
u"亿股":1,
u"亿美元":1,
u"亿份":1,
u"千":1,
u"万":1,
u"万元":1,
u"万美元":1,
u"万股":1,
u"万份":1,
u"万吨":1,
u"万桶":1,
u"万亩":1,
u"万起":1,
u"万人":1,
u"万人民币":1,
u"万人币":1,
u"万亿元":1,
u"万亿度":1,
u"万亿千瓦时":1,
u"%":1,
u"多亿":1,
u"多亿元":1,
u"多亿股":1,
u"多亿美元":1,
u"多亿份":1,
u"多万":1,
u"多万元":1,
u"多万美元":1,
u"多万股":1,
u"多万份":1,
u"倍":1,
u"天":1,
u"日":1,
u"年":1,
u"个":1,
u"家":1,
u"宗":1,
u"月":1,
u"月份":1
}

#usr_dict='/home/andy/my_tools/data/jieba_user.dict'
p = re.compile('^[a-zA-Z]+$')
p_num = re.compile('^[0-9\.]+$')
connect_symbol = {'-':1, '.':1, u'·':1, '~':1}
#num_suffix = seg_util.num_suffix

def seg_initial(usr_dict, segger=None):
    try:
        if None == segger:
            jieba.load_userdict(usr_dict)
        else:
            segger.load_userdict(usr_dict)
    except:
        s = "load jieba user dict [%s] fail. %s line:[%d]\n" % (usr_dict, __file__, sys._getframe().f_lineno)
        sys.stderr.write(s)
        return 1
    return 0

def seg_initial_bin(usr_dict, segger=None):
    word_list = common_bin_util.load_jieba_dict(usr_dict)
    if None == word_list:
        s = "load jieba user dict [%s] fail. %s line:[%d]\n" % (usr_dict, __file__, sys._getframe().f_lineno)
        sys.stderr.write(s)
        return 1
    for data in word_list:
        w = data[0]
        fre = data[1]
        if None == segger:
            jieba.add_word(w, fre)
        else:
            segger.add_word(w, fre)
    '''
    if usr_table != '':
        word_dict = {}
        for da in word_list:
            word_dict[da[0]] = da[1]
        try:
            dao = CommDao(usr_table)
            usr_data = dao.find_all()
        except Exception, ex:
            sys.stderr.write("%s:%s\n" % (Exception, ex))
            return 1
        for data in usr_data:
            if not(data['word'] in word_dict):
                jieba.add_word(data['word'], 100)
            if not(data['syno'] in word_dict):
                jieba.add_word(data['syno'], 100)
    '''
    return 0

def seg_initial_list(word_list, segger=None):
    for data in word_list:
        w = data[0]
        fre = data[1]
        if w is None or type(fre) is not int:
            continue
        if None == segger:
            jieba.add_word(w, fre)
        else:
            segger.add_word(w, fre)
    return 0

'''
def segment(txt):
    if len(txt) == 0:
        return None
    try:
        seg_list = jieba.cut(txt)
    except:
        return None
    fix_list = []
    flag = 0
    for term in seg_list:
        if p.match(term):
            '合并连续的英文字串'
            if flag == 0:
                fix_list.append(term)
            elif flag == 1:
                fix_list[-1] = fix_list[-1] + term
            flag = 1
        else:
            fix_list.append(term)
            flag = 0
    return fix_list
'''

def segment(txt, segger=None):
    if len(txt) == 0:
        return []
    try:
        if None == segger:
            seg_list = jieba.cut(txt)
        else:
            seg_list = segger.cut(txt)
    except:
        return None
    fix_list = []
    flag = 0
    term_list = []
    num_flag = 0
    for term in seg_list:
        term_list.append(term)
    for i in range(0, len(term_list)):
        term = term_list[i]
        if num_flag > 0:
            num_flag -= 1
            continue
        if p.match(term):
            '合并连续的英文字串'
            if flag == 0:
                fix_list.append(term)
            elif flag == 1:
                fix_list[-1] = fix_list[-1] + term
            flag = 1
        elif p_num.match(term):
            if i < len(term_list) - 1 and term_list[i+1] in num_suffix:
                fix_list.append(term + term_list[i+1])
                num_flag = 1
            elif i < len(term_list) - 2 and term_list[i+1] in connect_symbol and p_num.match(term_list[i+2]):
                fix_list.append(term + term_list[i+1] + term_list[i+2])
                num_flag = 2
                if i < len(term_list) - 3 and term_list[i+3] in num_suffix:
                    fix_list[-1] = fix_list[-1] + term_list[i+3]
                    num_flag += 1
            elif i < len(term_list) - 1 and p_num.match(term_list[i+1][0]):
                fix_list.append(term + term_list[i+1])
                num_flag = 1
            else:
                fix_list.append(term)
        else:
            fix_list.append(term)
            flag = 0
    return fix_list



