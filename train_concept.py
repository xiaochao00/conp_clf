#!/usr/bin/python
# coding=utf8
"""
# Author: andy
# Created Time : 2017-04-26 14:53:31

# File Name: topic_train.py
# Description:
# 概念提取的训练部分

"""

import sys
import os
import shutil
import json
import re
import math
import copy
import jieba
import traceback
import common_segment
import common_bin_util
import common_util
#from common_adaptor_dao import CommDao


class Worker:
    def __init__(self, parameter):
        # parameter:
        # {"seg_table":seg_table(可选), 'path':本地词典目录(必有)}
        # seg_table: 分词用的数据表
        self.initialed = 0
        self.conf = json.loads(parameter)
        self.cross_p = 10
        self.min_train_count = 50
        self.vocabulary = {}
        # self.sim_thresh = 0.1
        # self.max_wordid = 0
        '''
        if 'p' in self.conf:
            self.cross_p = self.conf['p']
        else:
            self.cross_p = 10
        if 'n' in self.conf:
            self.min_train_count = self.conf['n']
        else:
            self.min_train_count = 50
        if 'tid' in self.conf:
            self.tid = self.conf['tid']
        else:
            self.tid = ''
        '''
        if 'seg_table' in self.conf and self.conf['seg_table'] != None:
            self.seg_table = self.conf['seg_table']
        else:
            self.seg_table = ''
        if 'base_path' in self.conf and self.conf['base_path'] != None:
            self.data_path = self.conf['base_path']
        else:
            sys.stderr.write('need data path\n')
        if 'vocabulary' in self.conf and self.conf['vocabulary'] != None:
            self.vocabulary_path = self.conf['vocabulary']
        else:
            sys.stderr.write('need vocabulary path\n')
        self.db_jar_file = self.conf.get("db_jar_file")
        self.initial()

    def initial(self):
        '返回是否初始化成功'
        # 1:成功, 0:失败
        jieba_dict = self.data_path + '/jieba_user.dict.org.fil'

        # 分词初始化
        '''
        if segment.seg_initial_bin(jieba_dict, seg_table):
            sys.stderr.write("initial segment error\n")
            return 1
        sys.stderr.write("initial segment done\n")
        '''

        wfile = open(jieba_dict)
        word_list = []
        while 1:
            lines = wfile.readlines()
            if not lines:
                break
            for line in lines:
                line = line.decode('utf-8')
                line = line.rstrip('\n')
                tablist = line.split(' ')
                word_list.append([tablist[0], int(tablist[1])])
        wfile.close()
        #word_list = common_bin_util.load_jieba_dict(jieba_dict)
        if None == word_list:
            s = "load jieba user dict [%s] fail. %s line:[%d]\n" % (jieba_dict, __file__, sys._getframe().f_lineno)
            sys.stderr.write(s)
            return 1
        vfile = open(self.vocabulary_path)
        while 1:
            lines = vfile.readlines()
            if not lines:
                break
            for line in lines:
                line = line.decode('utf-8')
                line = line.rstrip('\n')
                tablist = line.split('\t')
                self.vocabulary[tablist[0]] = int(tablist[1])
        vfile.close()
        '''
        if self.seg_table != '':
            word_dict = {}
            for da in word_list:
                word_dict[da[0]] = da[1]
            try:
                dao = CommDao(self.seg_table, db_jar_file=self.db_jar_file)
                usr_data = dao.find_all()
            except Exception, ex:
                sys.stderr.write("%s:%s\n" % (Exception, ex))
                return 1
            for data in usr_data:
                if not (data['word'] in word_dict):
                    word_list.append([data['word'], 100])
                if not (data['name'] in word_dict):
                    word_list.append([data['name'], 100])
        '''
        try:
            self.segger = jieba.Tokenizer()
            if not common_segment.seg_initial_list(word_list, self.segger):
                sys.stderr.write("initial segment done\n")
            else:
                sys.stderr.write("initial segment error\n")
                return 1
        except Exception, ex:
            sys.stderr.write("%s, %s\n" % (Exception, ex))
            return 1

        self.initialed = 1
        return 0

    def get_data(self):
        # 从数据库输入数据
        if 'corpus_table' in self.conf:
            corpus_table = self.conf['train_data_news']
        else:
            corpus_table = ''
            sys.stderr.write("need configure[train_data_news]\n")
            return None

        try:
            dao = CommDao(corpus_table, self.db_jar_file)
            corpus_jstr = dao.find({'tid': self.tid}, limit=0)
            corpus_data = json.loads(corpus_jstr)
        except Exception, ex:
            sys.stderr.write("%s:%s\n" % (Exception, ex))
            return None
        news_list = []
        for data in corpus_data:
            if data['dtyp'] == 1:
                news = {'title': data['title'].lower(), 'id': str(data['_id']), 'content': data['content'].lower(),
                        'topic': {}}
                for tp in data['conp']:
                    news['topic'][tp] = 1
                news_list.append(news)
        return news_list

        '''
        conn = pymongo.MongoClient('192.168.250.208', 27017)
        db = conn['news']
        coll = db['crawler_news']#-----------------------------------------------------
        news_list = []
        task_id = self.conf['task_id']
        for data in coll.find({'tid':task_id}):
            if data['dtyp'] == 1:
                #训练用数据
                news = {'title':data['title'], 'id':data['_id'], 'content':data['content'], 'topic':{}}
                for tp in data['conp']:
                    news['topic'][tp] = 1
                news_list.append(news)
        return news_list
        '''

    def get_data_debug(self):
        # 用本地文件debug
        news_list = []
        # ifile = open('../data/tmp_train')
        ifile = open('tmp_train.seg.sample')
        while 1:
            lines = ifile.readlines()
            if not lines:
                break
            for line in lines:
                line = line.rstrip('\n')
                line = line.decode('utf-8')
                tablist = line.split('\t')
                news = {}
                news['id'] = tablist[0]
                news['title'] = ''
                news['content'] = tablist[2].lower()
                news['topic'] = {}
                if len(tablist) > 3:
                    for i in range(3, len(tablist)):
                        if tablist[i] != '':
                            news['topic'][tablist[i]] = 1
                news_list.append(news)
                news['seg'] = tablist[2].split(' ')
        ifile.close()
        return news_list

    def get_auc(self, sim_list):
        # 计算AUC值
        # input:
        # sim_list:[[sim, tag], ...]
        thresh = 1.0
        STEP = 0.01
        xy_list = []
        while thresh > 0.0:
            TP = 0  # 算法pos, 标注pos
            TN = 0  # 算法neg, 标注neg
            FP = 0  # 算法pos, 标注neg
            FN = 0  # 算法neg, 标注pos
            TPFN = 0  # 标注pos
            FPTN = 0  # 标注neg
            for da in sim_list:
                if da[0] > thresh and da[1] == 1:
                    TP += 1
                elif da[0] > thresh and da[1] == 0:
                    FP += 1
                if da[1] == 1:
                    TPFN += 1
                else:
                    FPTN += 1
            x = (FP + 0.0) / FPTN
            y = (TP + 0.0) / TPFN
            xy_list.append([x, y])
            thresh -= STEP
        xy_list.append([1.0, 1.0])  # thresh==0的情况
        auc = 0.0
        for i in range(0, len(xy_list) - 1):
            auc += (xy_list[i][1] + xy_list[i + 1][1]) * (xy_list[i + 1][0] - xy_list[i][0]) / 2
        return auc

    def get_avg_auc(self, auc_list):
        '计算平均auc'
        # input:
        # [auc, ... ]
        if len(auc_list) == 0:
            return 0.0
        avg_auc = 0.0
        for auc in auc_list:
            avg_auc += auc
        avg_auc = avg_auc / len(auc_list)
        return avg_auc

    def get_fea_auc(self, weight_list, fea_count, pos_valid_corpus, neg_valid_corpus):
        if fea_count == 0:
            return 0.0
        fea_vec = {}
        # 几何归一化
        '''
        print "len(weight_list):", len(weight_list)
        print "fea_count:", fea_count
        '''
        nor_sum = 0.0
        for i in range(0, fea_count):
            term = weight_list[i][0]
            weight = weight_list[i][1]
            fea_vec[term] = weight
            nor_sum += weight * weight
        nor_sum = math.sqrt(nor_sum)
        for t in fea_vec:
            fea_vec[t] = fea_vec[t] / nor_sum

        # 评估
        sim_list = []
        for doc in pos_valid_corpus:
            sim = common_util.cosine_txt(fea_vec, doc['tf_normal'], 1.0, 1.0)
            sim_list.append([sim, 1])
        for doc in neg_valid_corpus:
            sim = common_util.cosine_txt(fea_vec, doc['tf_normal'], 1.0, 1.0)
            sim_list.append([sim, 0])
        auc = self.get_auc(sim_list)
        return auc

    def search_best_parameter(self, pos_corpus, neg_corpus):

        pos_valid_cnt = len(pos_corpus) / self.cross_p
        neg_valid_cnt = len(neg_corpus) / self.cross_p
        auc_list = []
        best_fcnt_list = []
        best_feature = {}

        # 统计总的tf, df
        word_fre_all = {}
        for news in pos_corpus:
            for term in news['tf']:
                if not (term in word_fre_all):
                    word_fre_all[term] = {'pos_tf': 0, 'pos_df': 0, 'neg_tf': 0, 'neg_df': 0}
                word_fre_all[term]['pos_tf'] += news['tf'][term]
                word_fre_all[term]['pos_df'] += 1
        for news in neg_corpus:
            for term in news['tf']:
                if not (term in word_fre_all):
                    word_fre_all[term] = {'pos_tf': 0, 'pos_df': 0, 'neg_tf': 0, 'neg_df': 0}
                word_fre_all[term]['neg_tf'] += news['tf'][term]
                word_fre_all[term]['neg_df'] += 1

        # 交叉验证
        for i in range(0, self.cross_p):
            # 划分训练集和评估集
            # 正例
            '''
            pos_train_corpus = []
            if i > 0:
                pos_train_corpus.extend(pos_corpus[pos_valid_cnt*(i-1):pos_valid_cnt*i])
            pos_train_corpus.extend(pos_corpus[pos_valid_cnt*(i+1):])
            '''
            pos_valid_corpus = pos_corpus[pos_valid_cnt * i:pos_valid_cnt * (i + 1)]

            # 负例
            '''
            neg_train_corpus = []
            if i > 0:
                neg_train_corpus.extend(neg_corpus[neg_valid_cnt*(i-1):neg_valid_cnt*i])
            neg_train_corpus.extend(neg_corpus[neg_valid_cnt*(i+1):])
            '''
            neg_valid_corpus = neg_corpus[neg_valid_cnt * i:neg_valid_cnt * (i + 1)]

            pos_DF = len(pos_corpus)
            neg_DF = len(neg_corpus)

            # 从全量中减去验证集的部分, 得到训练集数据
            word_fre = copy.deepcopy(word_fre_all)
            for news in pos_valid_corpus:
                for term in news['tf']:
                    if not (term in word_fre):
                        word_fre[term] = {'pos_tf': 0, 'pos_df': 0, 'neg_tf': 0, 'neg_df': 0}
                    word_fre[term]['pos_tf'] -= news['tf'][term]
                    word_fre[term]['pos_df'] -= 1
            for news in neg_valid_corpus:
                for term in news['tf']:
                    if not (term in word_fre):
                        word_fre[term] = {'pos_tf': 0, 'pos_df': 0, 'neg_tf': 0, 'neg_df': 0}
                    word_fre[term]['neg_tf'] -= news['tf'][term]
                    word_fre[term]['neg_df'] -= 1

            # 算出向量
            weight_list = []
            fea_df_thresh = 3  # 至少有超过三篇新闻中出现了，才计算入特征
            for term in word_fre:
                if word_fre[term]['pos_df'] < fea_df_thresh:
                    continue
                w_tf = (word_fre[term]['pos_tf'] + 1) / (word_fre[term]['neg_tf'] + 1)
                w_df = (word_fre[term]['pos_df'] + 1) / (word_fre[term]['neg_df'] + 1)
                weight = (w_tf + w_df) * word_fre[term]['pos_df'] / pos_DF
                weight_list.append([term, weight])
            weight_list.sort(key=lambda d: d[1], reverse=True)

            # 搜索最佳特征数量
            min_fea_count = 10  # 中心向量长度从30搜索到100
            max_fea_count = 100
            if len(weight_list) < max_fea_count:
                max_fea_count = len(weight_list)

            '''
            s = ''
            for i in range(0, max_fea_count):
                t = weight_list[i][0]
                print ("%s\t%f\t%d\t%d\t%d\t%d" % (weight_list[i][0], weight_list[i][1], word_fre[t]['pos_tf'], word_fre[t]['pos_df'], word_fre[t]['neg_tf'], word_fre[t]['neg_df'])).encode('utf-8')
            '''

            fea_count = min_fea_count
            valid_res_list = []
            step = 10
            # 以step为步长, 找出初步最优参数
            while fea_count < max_fea_count:
                if fea_count > len(weight_list):
                    break
                auc = self.get_fea_auc(weight_list, fea_count, pos_valid_corpus, neg_valid_corpus)

                valid_res_list.append({'fea_count': fea_count, 'auc': auc})
                # print "fea_count:%d, auc:%f" % (fea_count, auc)
                fea_count += step
            max_auc = 0.0
            max_auc_fcnt = 0
            for i in range(0, len(valid_res_list)):
                vr = valid_res_list[i]
                if vr['auc'] > max_auc:
                    max_auc = vr['auc']
                    max_auc_fcnt = vr['fea_count']

            # 向特征数量增加的方向搜索
            step = 1
            last_auc = max_auc
            h_auc = last_auc
            h_fea_cnt = max_auc_fcnt
            for k in range(0, 10):
                fea_count = max_auc_fcnt + step * k
                if fea_count > len(weight_list):
                    break
                auc = self.get_fea_auc(weight_list, fea_count, pos_valid_corpus, neg_valid_corpus)
                # print "fea_count:%d, auc:%f" % (fea_count, auc)

                if auc < last_auc:
                    # auc一旦下降就停止搜索
                    break
                if auc > h_auc:
                    h_auc = auc
                    h_fea_cnt = fea_count
                last_auc = auc

            # 向特征数量减少的方向搜索
            last_auc = max_auc
            l_auc = last_auc
            l_fea_cnt = max_auc_fcnt
            for k in range(0, 10):
                fea_count = max_auc_fcnt - step * k
                auc = self.get_fea_auc(weight_list, fea_count, pos_valid_corpus, neg_valid_corpus)
                # print "fea_count:%d, auc:%f" % (fea_count, auc)
                if auc < last_auc:
                    # auc一旦下降就停止搜索
                    break
                if auc > l_auc:
                    l_auc = auc
                    l_fea_cnt = fea_count
                last_auc = auc

            if h_auc > l_auc:
                best_fea_cnt = h_fea_cnt
                best_auc = h_auc
            else:
                best_fea_cnt = l_fea_cnt
                best_auc = l_auc

            auc_list.append(best_auc)
            best_fcnt_list.append(best_fea_cnt)
            # print "best_fea_count:%d, best_auc:%f" % (best_fea_cnt, best_auc)
            # 记录下best_fea_count对应的特征及best_auc
            for j in range(0, best_fea_cnt):
                fea = weight_list[j][0]
                wit = weight_list[j][1]
                if not (fea in best_feature):
                    best_feature[fea] = {'fea': fea, 'cnt': 0, 'weight': 0.0}
                best_feature[fea]['cnt'] += 1
                best_feature[fea]['weight'] += wit * best_auc

        return best_feature

    def train(self, parameter):
        try:
            return self.do_train(parameter)
        except Exception as ex:
            print ex
            traceback.print_exc(file=sys.stdout)
            raise Exception('train error', traceback.format_exc())

    def do_train(self, input_jstr):
        '主函数'
        # input_jstr:
        # {"data":[{"title":"t","content":"content","conp":[conp1,]}], "config":{"p":"p", "n":"n", "path":"old_model_path", "concepts":[需要训练的概念], "tid":task_id}}
        # "p":fold count, 默认值为10, 可选
        # "n":min_train_count, 默认值为50, 可选
        # "old_model_path":旧model的路径,绝对路径/相对路径均可, 可选, 但一般情况下应该有
        # "concepts":指定的需要训练的概念, 如果没有该参数，则对输入语料中的所有概念都进行训练。如果设定了该参数，且没有设定"n"参数，则"n"的默认值为1。可选
        # "tid":task id, 必有
        # 初始化
        if self.initialed == 0:
            sys.stderr.write("not initialized\n")
            return {'message': None, 'stat': 1}

        # 输入语料
        '''
        if debug_flag == 1:
            news_list = self.get_data_debug()   #用本地文件做测试用
        else:
            news_list = self.get_data()   #正式运行用
        '''
        news_list = []
        old_model = {}
        input_data = json.loads(input_jstr)
        conp_id = input_data.get('conp_id', 0)

        for data in input_data['data']:
            news = {'title': data['title'].lower(), 'content': data['content'].lower(), 'topic': {}}
            for tp in data['conp']:
                news['topic'][tp] = 1
            if 'seg' in data:
                news['seg'] = data['seg']
            news_list.append(news)
        print ('config:'), input_data.get('config')
        if 'path' in input_data['config'] and input_data['config']['path'] != None:
            old_model_bin = input_data['config']['path'] + '/' + 'conp_vec.bin'
            old_model = common_bin_util.load_txt_vec(old_model_bin, utf8_flag=1)
            if None == old_model:
                sys.stderr.write("load old model[%s] error\n" % (old_model_bin))
                return {'message': None, 'stat': 1}
        if 'p' in input_data['config'] and input_data['config']['p'] is not None:
            self.cross_p = input_data['config']['p']
        else:
            self.cross_p = 10
        if 'n' in input_data['config'] and input_data['config']['n'] is not None:
            self.min_train_count = input_data['config']['n']
        else:
            self.min_train_count = 50
        if 'tid' in input_data['config'] and input_data['config']['tid'] != None:
            self.tid = input_data['config']['tid']
        else:
            self.tid = ''

        # 建立输出目录
        self.model_path = "%s/%s/%s_%d_%d/" % (
        self.data_path, 'model_1vo', self.tid, self.cross_p, self.min_train_count)
        if os.path.exists(self.model_path):
            # shutil.rmtree(self.model_path)
            pass
        else:
            os.mkdir(self.model_path)
        self.word_list_file = self.model_path + 'word_dict.bin'
        self.model_vec_file = self.model_path + 'conp_vec.bin' + str(conp_id)

        self.concept_trained = None
        if 'concepts' in input_data['config'] and input_data['config']['concepts'] != None:
            self.concept_trained = {}
            for c in input_data['config']['concepts']:
                self.concept_trained[c] = 1
            if not ('n' in input_data['config']):
                self.min_train_count = 1

        sys.stderr.write("get data done\n")

        p_term = re.compile("^[#&@$\.+0-9]+$")
        p_hanzi = re.compile(u'[\u3400-\u9fa5]')
        p_eng = re.compile('[a-zA-Z]+')

        # 分词并统计topic分布, 统计tf
        tp_cnt_dict = {}
        idx = 0
        for news in news_list:
            if not ('seg' in news):
                seg_list = common_segment.segment(news['title'] + '#&#' + news['content'], self.segger)
                # ofile.write(("%s\t%s\t%s\t%s\n" % (news['id'], news['title'], ' '.join(seg_list), '\t'.join(news['topic'].keys()))).encode('utf-8'))
            else:
                seg_list = news['seg']

            tmp_dict = {}
            tf_sum = 0.0
            for term in seg_list:
                # if term in self.word_dict:
                if p_hanzi.search(term) is None and p_eng.match(term) is None:
                    continue
                if term not in self.vocabulary:
                    continue
                if len(term) > 1 and not (p_term.match(term)):
                    # wid = self.word_dict[term]
                    if not (term in tmp_dict):
                        tmp_dict[term] = 0
                    tmp_dict[term] += 1.0
            news['tf'] = tmp_dict

            for term in tmp_dict:
                tf_sum += tmp_dict[term] * tmp_dict[term]
            tf_sum = math.sqrt(tf_sum)

            # 几何归一化
            tmp_normal_dict = {}
            for term in tmp_dict:
                tmp_normal_dict[term] = tmp_dict[term] / tf_sum
            news['tf_normal'] = tmp_normal_dict

            # news['seg'] = seg_list
            for tp in news['topic']:
                if not (tp in tp_cnt_dict):
                    tp_cnt_dict[tp] = 0
                tp_cnt_dict[tp] += 1
            idx += 1
            if idx % 1000 == 0:
                sys.stderr.write("segment %d\n" % (idx))
        sys.stderr.write("tf done\n")

        # vec_file = open('fea_vec', 'w')

        fea_vec_all = {}
        # 计算每个topic
        for tp in tp_cnt_dict:
            if None != self.concept_trained:
                # 有指定的概念
                if not (tp in self.concept_trained):
                    continue
            if tp_cnt_dict[tp] < self.min_train_count:
                sys.stderr.write(("%s: %d, skip\n" % (tp, tp_cnt_dict[tp])).encode('utf-8'))
                continue
            sys.stderr.write(("%s: %d, run\n" % (tp, tp_cnt_dict[tp])).encode('utf-8'))
            pos_corpus = []
            neg_corpus = []
            for news in news_list:
                if tp in news['topic']:
                    pos_corpus.append(news)
                else:
                    neg_corpus.append(news)
            sys.stderr.write("pos_cnt:%d, neg_cnt:%d\n" % (len(pos_corpus), len(neg_corpus)))

            if len(pos_corpus) < self.cross_p:
                sys.stderr.write(("%s: %d, skip, pos_corpus\n" % (tp, len(pos_corpus))).encode('utf-8'))
                continue
            best_feature = self.search_best_parameter(pos_corpus, neg_corpus)
            fea_vec = {}
            f_sum = 0.0
            for fea in best_feature:
                weight = best_feature[fea]['weight'] / best_feature[fea]['cnt']
                fea_vec[fea.encode('utf-8')] = weight
                f_sum += weight * weight
            f_sum = math.sqrt(f_sum)
            for fea in fea_vec:
                fea_vec[fea] = fea_vec[fea] / f_sum

            fea_vec_sort = sorted(fea_vec.iteritems(), key=lambda d: d[1], reverse=True)
            '''
            s = tp
            for da in fea_vec_sort:
                s = "%s\t%s\t%f" % (s, da[0].decode('utf-8'), da[1])
            vec_file.write((s + '\n').encode('utf-8'))
            sys.stderr.write((s + '\n').encode('utf-8'))
            '''

            # 用全部数据训练一遍
            # fea_vec = self.train(pos_corpus, neg_corpus, best_feature)
            fea_vec_all[tp.encode('utf-8')] = fea_vec

        # vec_file.close()
        # 合并旧的model
        for tp in old_model:
            if not (tp in fea_vec_all):
                fea_vec_all[tp] = old_model[tp]

        # 返回模型，在外部进行合并后再保存
        return fea_vec_all

        if common_bin_util.write_txt_vec(fea_vec_all, self.model_vec_file):
            sys.stderr.write("output model_vec[%s] error\n" % (self.model_vec_file))
            return json.dumps({'message': None, 'stat': 1})

        '''
        #输出
        fea_vec_dict = {}
        for tp in fea_vec_all:
            vec = fea_vec_all[tp]
            vec_output = []
            for fea in vec:
                if fea in self.word_dict:
                    fid = self.word_dict[fea]
                else:
                    self.max_wordid += 1
                    fid = self.max_wordid
                    self.word_dict[fea] = fid
                    self.word_list.append([fea.encode('utf-8'), fid])
                vec_output.append([fid, vec[fea]])
            fea_vec_dict[tp.encode('utf-8')] = vec_output

        if common_bin_util.write_word_dict(self.word_list, self.word_list_file):
            sys.stderr.write("output word_dict[%s] error\n" % (self.word_list_file))
            return 1
        if common_bin_util.write_vec(fea_vec_dict, self.model_vec_file):
            sys.stderr.write("output model_vec[%s] error\n" % (self.model_vec_file))
            return 1
        '''

        return json.dumps({'message': self.model_path, 'stat': 0})

def tag_train(data_list, tag=None, conp_id=0):
    # {"data":[{"title":"t","content":"content","conp":[conp1,]}], "config":{"p":"p", "n":"n", "path":"old_model_path", "concepts":[需要训练的概念], "tid":task_id}}
    initial_confg = {}
    initial_confg['base_path'] = '../data/'
    #initial_confg['vocabulary'] = '../data/data0/vocabulary.0'
    initial_confg['vocabulary'] = '../data/vocabulary'
    initial_jstr = json.dumps(initial_confg)
    # {"seg_table":seg_table(可选), 'path':本地词典目录(必有)}
    tr = Worker(initial_jstr)

    config = {}
    config['p'] = 10
    config['n'] = 15
    if tag is not None:
        config['concepts'] = [tag]
    else:
        return None
    #config['concepts'] = ['0_2_0_0']
    config['tid'] = 'no_tid'
    # "p":fold count, 默认值为10, 可选
    # "n":min_train_count, 默认值为50, 可选
    # "old_model_path":旧model的路径,绝对路径/相对路径均可, 可选, 但一般情况下应该有
    # "concepts":指定的需要训练的概念, 如果没有该参数，则对输入语料中的所有概念都进行训练。如果设定了该参数，且没有设定"n"参数，则"n"的默认值为1。可选
    # "tid":task id, 必有
    input_jstr = json.dumps({'data':data_list, 'config':config, 'conp_id':conp_id})
    return tr.do_train(input_jstr)




if __name__ == '__main__':
    # test
    para = {}
    para['seg_table'] = 'csf_corpus.nlp_dict_entity'
    para['base_path'] = '../config/train_concept/'
    parameter = json.dumps(para)
    tr = Worker(parameter)

    # 用本地文件debug
    news_list = []
    ifile = open('../config/train_concept/test.txt')
    while 1:
        lines = ifile.readlines()
        if not lines:
            break
        for line in lines:
            line = line.rstrip('\n')
            line = line.decode('utf-8')
            tablist = line.split('\t')
            news = {}
            news['title'] = tablist[1]
            news['content'] = tablist[2]
            news['conp'] = {}
            if len(tablist) > 3:
                for i in range(3, len(tablist)):
                    if tablist[i] != '':
                        news['conp'][tablist[i]] = 1
            # news['seg'] = tablist[2].split(' ')
            news_list.append(news)
    ifile.close()
    run_para = {'tid': '001', 'p': 10, 'n': 50, 'path': '../config/train_concept/model_old/'}
    input_jstr = json.dumps({'data': news_list, 'config': run_para})
    rs = tr.train(input_jstr)
    print ("rs:"), rs
