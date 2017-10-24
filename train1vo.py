#!/usr/bin/python
#coding=utf8
"""
# Author: andy
# Created Time : 2017-10-12 16:37:01

# File Name: train1vo.py
# Description:
# 用概念分类的方法对文本分类，这是个1vo的方法

"""
import sys
import re
import copy
import random
import json
import traceback

import xlrd
import jieba
import datetime
import train_concept
import match_concept
import common_bin_util
import full2half


def load_corpus(pos_corpus, neg_corpus):
    # 分别读取正例和负例语料
    # input:
    # pos_corpus:正例语料文件
    # neg_corpus:负例语料文件
    # output:
    # pos_raw_data:[{'title':title, 'content':content, 'conp':[conp, ]}, ], conp的意思是该篇语料可以作为哪些主题的正例
    # neg_raw_data:[{'title':title, 'content':content, 'neg_conp':[neg_conp, ]}, ], neg_conp的意思是该篇语料可以作为哪些主题的负例

    # 读正例语料
    p_newline = re.compile('[\n\r]')
    p_tab = re.compile('\t')
    pos_list = load_xlsx(pos_corpus)
    pos_raw_data = []
    for row in pos_list:
        title = full2half.full2half(row[1])
        title = p_newline.sub('', title)
        content = full2half.full2half(row[2])
        content = p_newline.sub('#&#', content)
        content = p_tab.sub('|+|', content)
        pos_raw_data.append({'title':title, 'content':content, 'conp':row[0].split('|')})

    # 读负例语料
    p_decimal = re.compile('\d\.\d+')
    neg_raw_data = []
    cfile = open(neg_corpus)
    while 1:
        lines = cfile.readlines()
        if not lines:
            break
        for line in lines:
            line = line.decode('utf-8')
            line = line.rstrip('\n')
            tablist = line.split('\t')
            if len(tablist) != 3:
                continue
            title = tablist[1]
            content = '\t'.join(tablist[2:])
            '''
            if p_decimal.search(content):
                continue
            '''
            if tablist[0] == '':
                tags = []
            else:
                tags = tablist[0].split('|')
            neg_raw_data.append({'title':title, 'content':content, 'neg_conp':tags})
    cfile.close()
    #print 'len(raw_data):', len(raw_data)
    global seg_buffer
    seg_buffer = [[]] * len(neg_raw_data)
    return pos_raw_data, neg_raw_data


def load_xlsx(fname, sheet_id=0):
    #读取xlsx文件的内容(标注数据)
    #input:
    #fname:文件路径
    #sheet_id:表的id, 从0开始
    #output:
    #row_list:xlsx内容, 每个元素是一行的内容 [[col1, col2, col3,...],...]
    try:
        workbook = xlrd.open_workbook(fname)
    except Exception, ex:
        print Exception, ex
        traceback.print_exc()
    booksheet = workbook.sheet_by_index(sheet_id)
    row_list = []
    # 数据从第2行开始
    for row in range(1,booksheet.nrows):
        col_list = []
        for col in range(booksheet.ncols):
            cel = booksheet.cell(row, col)
            val = cel.value
            col_list.append(val)
            #print val.encode('utf-8')
        row_list.append(col_list)
    # for row in row_list:
    #    print ('\t'.join(row)).encode('utf-8')
    return row_list


# 负例语料的分词缓存
seg_buffer = []
def train_1vo(pos_raw_data, neg_raw_data, conp_list, only_title_list, model_vec_file):
    # 训练1vo模型
    # intput:
    # pos_raw_data:正例语料list, [{'title':'', 'content':content, 'conp':[conp,]}, ]
    # neg_raw_data:负例语料list, [{'title':'', 'content':content, 'neg_conp':[neg_conp,]}, ]
    # conp_list:类别名称list

    global local_segger
    global seg_buffer

    # 选择的负例语料数量
    neg_count = 10000

    conp_id = 0
    fea_vec_all = {}
    for i in range(len(conp_list)):
        conp = conp_list[i]
        only_title = only_title_list[i]
        raw_data = []
        # 挑选正例语料
        #print(conp.encode('utf-8'), type(conp))
        #print(len(pos_raw_data))
        for data in pos_raw_data:
            conps = data['conp']
            for cp in conps:
                #print(cp.encode('utf-8'), type(cp))
                if cp == conp:
                    data_new = {}
                    data_new['title'] = data['title']
                    if only_title == 0:
                        data_new['content'] = data['content']
                        data_new['seg'] = list(local_segger.cut(data_new['title'] + '#&#' + data_new['content']))
                    else:
                        data_new['content'] = ''
                        data_new['seg'] = list(local_segger.cut(data_new['title']))
                    data_new['conp'] = [conp]
                    raw_data.append(data_new)
                    break
        pos_cnt = len(raw_data)
        # 挑选负例语料
        neg_id = 0
        for data in neg_raw_data:
            if random.randint(1, len(neg_raw_data)) > neg_count:
                neg_id += 1
                continue
            conps = data['neg_conp']
            for cp in conps:
                if cp == conp:
                    data_new = {}
                    data_new['title'] = data['title']
                    if not seg_buffer[neg_id]:
                        # 记入分词结果缓存
                        all_seg = list(local_segger.cut(data_new['title'] + '#&#' + data['content']))
                        title_seg = list(local_segger.cut(data_new['title']))
                        seg_buffer[neg_id] = [title_seg, all_seg]

                    if only_title == 0:
                        data_new['content'] = data['content']
                        data_new['seg'] = seg_buffer[neg_id][1]
                    else:
                        data_new['content'] = ''
                        data_new['seg'] = seg_buffer[neg_id][0]
                    data_new['conp'] = []
                    raw_data.append(data_new)
                    #print(('|'.join(data_new['conp']) + '\t' + data_new['content']).encode('utf-8'))
                    break
            neg_id += 1

        neg_cnt = len(raw_data) - pos_cnt
        print('pos count:', pos_cnt)
        print('neg count:', neg_cnt)

        # 训练
        fea_vec = train_concept.tag_train(raw_data, conp, conp_id)
        for key in fea_vec:
            fea_vec_all[key] = fea_vec[key]
        '''
        model_jstr = train_concept.tag_train(raw_data, conp, conp_id)
        if model_jstr is None:
            print('%s training error.' % (conp.encode('utf-8')))
            continue
        print model_jstr
        model_data = json.loads(model_jstr)
        print model_data
        '''
        conp_id += 1

    # 输出模型
    if common_bin_util.write_txt_vec(fea_vec_all, model_vec_file):
        sys.stderr.write("output model_vec[%s] error\n" % (model_vec_file))
        return 1
    return 0


def predict_class(txt_list, sim_thresh=0.08):
    # 预测输入数据的主题
    # input:
    # txt_list:[{'title':title, 'content':content}, ], 待预测的数据
    # sim_thresh:过滤阈值, 相关度大于此阈值的主题结果才会输出
    # output:
    # 主题分类结果: [{'list':[{'name':conp_name, 'sim':sim}, ]}, ]

    # 数据路径
    base_path = '../data/'
    # 模型路径
    model_path = '../data/model_1vo/no_tid_10_50/'
    # 词表路径
    vocabulary = '../data/vocabulary'
    # 主题配置
    conp_file = '../data/conp_list'

    parameter = {'base_path':base_path, 'model_path':model_path, 'vocabulary':vocabulary, 'conp_file':conp_file}
    input_jstr = json.dumps(parameter)
    sim_thresh = 0.08

    # 分类器实例
    worker = match_concept.Worker(input_jstr)
    # 分类器输入数据格式
    raw_data = []
    i = 0
    for txt_data in txt_list:
        '''
        p_list = txt.split('#&#')
        t_list = txt.split('\t')
        if i == 1:
            # only use title and 1st paragraph
            raw_data.append({'data':{'title':'', 'content':'#&#'.join(p_list[0:2])}, 'config':{'t':sim_thresh}})
        else:
            # use all content
            raw_data.append({'data':{'title':'', 'content':txt}, 'config':{'t':sim_thresh}})
        '''
        raw_data.append({'data':{'title':txt_data['title'], 'content':txt_data['content']}, 'config':{'t':sim_thresh}})
        i += 1
    #input_jstr = json.dumps({'data':raw_data, 'config':{'t':sim_thresh}})
    input_jstr = json.dumps(raw_data)
    # 分类
    res_jstr = worker.process(input_jstr)
    res_data = json.loads(res_jstr)
    '''
    res_jstr = worker.valid(input_jstr)
    res_data = json.loads(res_jstr)
    '''
    return res_data['message']


def class_valid(raw_data):
    base_path = '../data/data0/'
    model_path = '../data/data0/model_1vo/no_tid_10_50/'
    parameter = {'base_path':base_path, 'model_path':model_path}
    input_jstr = json.dumps(parameter)
    #sim_thresh = 0.08
    sim_thresh = 0.0001

    worker = match_concept.Worker(input_jstr)
    '''
    raw_data = []
    for txt in txt_list:
        raw_data.append({'title':'', 'content':txt})
    '''
    '''
    input_data = []
    for raw in raw_data:
        input_data.append({'data':raw, 'config':{'t':sim_thresh}})
    input_jstr = json.dumps(input_data)
    '''
    input_jstr = json.dumps({'data':raw_data, 'config':{'t':sim_thresh}})
    #res_jstr = worker.process(input_jstr)
    #res_data = json.loads(res_jstr)
    res_jstr = worker.validate(input_jstr)
    res_data = json.loads(res_jstr)
    print res_data['message']
    return res_data['message']


def load_conp(conp_file):
    # 读取分类体系及是否只使用title
    # input:conp_file:conp表, 格式为 conp'\t'only_title(0/1/2, 0表示用title加全文, 1表示只用title, 2表示用title加全文的第一段)
    # output:
    # conp_list:[conp_name, ], conp名称的list
    # only_title_list:[only_title, ], only_title标志的list, 和conp_list一一对应
    conp_list = []
    only_title_list = []

    cfile = open(conp_file)
    for line in cfile.readlines():
        line = line.decode('utf-8')
        line = line.rstrip('\n')
        tlist = line.split('\t')
        conp_list.append(tlist[0])
        only_title_list.append(int(tlist[1]))
    cfile.close()
    return conp_list, only_title_list


if __name__ == '__main__':
    #pos_corpus_file = '../data/pos.xlsx'
    #pos_corpus_file = '../data/pos4.xlsx'
    #pos_corpus_file = '../data/pos4_1.xlsx'
    # 正例语料文件
    pos_corpus_file = '../data/pos_1013.xlsx'
    # 负例语料文件
    neg_corpus_file = '../data/neg_corpus.2'
    # 模型文件
    model_vec_file = '../data/model_1vo/no_tid_10_50/conp_vec.bin'
    # 主题类别配置
    conp_file = '../data/conp_list'

    sta_time = datetime.datetime.now()

    # 初始化分词
    jieba_dict = '../data/jieba_user.dict.org.fil'
    local_segger = jieba.Tokenizer()
    local_segger.load_userdict(jieba_dict)

    '''
    #conp_list = [u'CPI', u'PPI'] #---------------------------------
    conp_list = [u'CPI', u'PPI', u'经济表现'] #---------------------------------
    #conp_list = [u'PPI'] #---------------------------------
    only_title_list = [0, 0, 1]
    '''
    conp_list, only_title_list = load_conp(conp_file)

    '''
    # test for some conp
    model_vec_file = '../data/model_1vo/no_tid_10_50/conp_vec.bin4'
    conp_list = [u'沙尘暴'] #---------------------------------
    only_title_list = [0]
    '''

    pos_raw_data, neg_raw_data = load_corpus(pos_corpus_file, neg_corpus_file)
    # raw_data = load_corpus(corpus_file)
    sys.stderr.write("load corpus done\n")

    train_flag = 1

    if train_flag == 1:
        # 训练
        train_1vo(pos_raw_data, neg_raw_data, conp_list, only_title_list, model_vec_file)
    elif train_flag == 0:
        # 用正例语料进行测试
        tag_list = []
        txt_list = []
        for data in pos_raw_data:
            #txt_list.append(data['title'] + '\t' + data['content'])
            txt_list.append({'title':data['title'], 'content': data['content']})
            tag_list.append(data['conp'])
        res_list = predict_class(txt_list)
        for i in range(len(tag_list)):
        #for i in range(len(txt_list)):
            res_str = ''
            for conp_res in res_list[i]['list']:
                res_str = "%s|%s %0.4f" % (res_str, conp_res['name'], conp_res['sim'])
            res_str = res_str.lstrip('|')
            #print tag_list[i], res_list[i], txt_list[i].encode('utf-8')
            print ("%s\t%s\t%s\t%s" % (tag_list[i][0], res_str, txt_list[i]['title'], txt_list[i]['content'])).encode('utf-8')
            #print(res_list[i], tag_list[i]), txt_list[i].encode('utf-8')
            #print(res_list[i], tag_list[i])
    elif train_flag == 2:
        pass
        '''
        txt_list = []
        tfile = open('../data/test.neg2')
        for line in tfile.readlines():
            line = line.decode('utf-8')
            line = line.rstrip('\n')
            txt_list.append(line)
        tfile.close()
        res_list = predict_class(txt_list)
        for i in range(len(txt_list)):
            print res_list[i], txt_list[i].encode('utf-8')
        '''
    elif train_flag == 3:
        # 用指定的文本数据语料进行测试
        txt_list = []
        tag_list = []
        #tfile = open('../data/pos.4.1')
        #tfile = open('../data/neg.4.1')
        tfile = open('../data/test')
        for line in tfile.readlines():
            line = line.decode('utf-8')
            line = line.rstrip('\n')
            tlist = line.split('\t')
            #txt_list.append('\t'.join(tlist[1:]))
            txt_list.append({'title':tlist[1], 'content':tlist[2]})
            tag_list.append(tlist[0])
        tfile.close()
        res_list = predict_class(txt_list)
        for i in range(len(txt_list)):
            res_str = ''
            for conp_res in res_list[i]['list']:
                res_str = "%s|%s %0.4f" % (res_str, conp_res['name'], conp_res['sim'])
            res_str = res_str.lstrip('|')
            #print tag_list[i], res_list[i], txt_list[i].encode('utf-8')
            print ("%s\t%s\t%s\t%s" % (tag_list[i], res_str, txt_list[i]['title'], txt_list[i]['content'])).encode('utf-8')

    end_time = datetime.datetime.now()
    sys.stderr.write("run:%s\n" % (str(end_time - sta_time)))


