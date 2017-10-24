#!/usr/bin/python
#coding=utf-8
import json
import logging
import logging.handlers
import math
import re
import sys
import jieba

import common_bin_util
import common_segment
#from common_adaptor_dao import CommDao

"""
提取概念
"""

bad_class_data = {}
class_data = {}
match_dict = {}
logger = None
stock_thresh = 0.15
sim_thresh = 0.1
word_dict = {}
p_term = re.compile("^[#&@$\.+0-9]+$")
segger = None
vocabulary = {}


#def topic_initial(conf_file):
def topic_initial(input_jstr):

    input_data = json.loads(input_jstr)

    if 'base_path' in input_data and input_data['base_path'] != None:
        data_path = input_data['base_path'] + '/'
    else:
        sys.stderr.write("need data path\n")
        return 1
    if 'model_path' in input_data and input_data['model_path'] != None:
        model_path = input_data['model_path'] + '/'
    else:
        sys.stderr.write("need data path\n")
        return 1
    vocabulary_file = data_path + '/' + input_data.get('vocabulary')
    if vocabulary_file is None:
        sys.stderr.write("need vocabulary file\n")
        return 1
    global vocabulary
    vocabulary = load_vocabulary(vocabulary_file)
    global sim_thresh
    global stock_thresh

    class_vec_file_bin = model_path + 'conp_vec.bin'
    #seg_usr_dict_bin = data_path + 'jieba_user.dict.bin'
    jieba_dict = data_path + '/jieba_user.dict.org.fil'
    '''
    bad_class_vec_file_bin = data_path + 'bad_vec.bin'
    conp_word_file_bin = data_path + 'conp_words.bin'
    worddict_bin = data_path + 'word_dict.bin'
    '''
    log_file = data_path + 'txt_topic.log'

    '''
    topic_kw_table = ''
    if 'topic_kw_table' in input_data and input_data['topic_kw_table'] != None:
        topic_kw_table = input_data['topic_kw_table']
    topic_name_table = ''
    if 'topic_name_table' in input_data and input_data['topic_name_table'] != None:
        topic_name_table = input_data['topic_name_table']
    seg_table = ''
    if 'seg_table' in input_data and input_data['seg_table'] != None:
        seg_table = input_data['seg_table']
    '''

    handler = logging.handlers.RotatingFileHandler(log_file, maxBytes = 1024*1024, backupCount = 3) # 实例化handler 
    fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'

    formatter = logging.Formatter(fmt)   # 实例化formatter
    handler.setFormatter(formatter)      # 为handler添加formatter
    global logger
    logger = logging.getLogger('txt_topic')    # 获取名为tst的logger
    logger.addHandler(handler)           # 为logger添加handler
    logger.setLevel(logging.DEBUG)

    logger.info("initial start")

    '''
    try:
        if not txt2vec.load_worddict_bin(worddict_bin):
            logger.info("initial txt2vec done")
        else:
            logger.info("initial txt2vec error")
            return 1
    except Exception,ex:
        logger.info("%s, %s" % (Exception, ex))
        return 1
    '''
    global bad_class_data
    global class_data
    '''
    try:
        bad_class_data = load_class_bin(bad_class_vec_file_bin)
        if None != bad_class_data:
            logger.info("initial class_vec bad done")
        else:
            logger.info("initial class_vec bad error")
            return 1
    except Exception,ex:
        logger.info("%s, %s" % (Exception, ex))
        return 1
    '''
    #try:
    class_data = load_class_bin(class_vec_file_bin)
    if None != class_data:
        logger.info("initial class_vec done")
    else:
        logger.info("initial class_vec error")
        return 1
    '''
    for i in range(0, len(class_data)):
        vec = class_data['vec'][i]
        s = class_data['name'][i]
        for k in vec:
            s = "%s %s:%f" % (s, k.encode('utf-8'), vec[k])
        print s
    '''

    # 读取conp的计算方式
    conp_file = data_path + '/' + input_data.get('conp_file')
    if conp_file is None:
        sys.stderr.write("need conp_file\n")
        return 1
    class_data['head_flag'] = [0] * len(class_data['name'])
    cfile = open(conp_file)
    for line in cfile.readlines():
        line = line.decode('utf-8')
        line = line.rstrip('\n')
        tlist = line.split('\t')
        conp = tlist[0].encode('utf-8')
        head_flag = int(tlist[1])
        for i in range(len(class_data['name'])):
            if class_data['name'][i] == conp:
                class_data['head_flag'][i] = head_flag
    cfile.close()

    '''
    except Exception,ex:
        logger.info("%s, %s" % (Exception, ex))
        return 1
    '''

    #word_list = common_bin_util.load_jieba_dict(seg_usr_dict_bin)
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
    if None == word_list:
        s = "load jieba user dict [%s] fail. %s line:[%d]\n" % (jieba_dict, __file__, sys._getframe().f_lineno)
        sys.stderr.write(s)
        return 1
    '''
    if seg_table != '':
        word_dict = {}
        for da in word_list:
            word_dict[da[0]] = da[1]
        try:
            dao = CommDao(seg_table)
            usr_data = dao.find_all()
        except Exception, ex:
            sys.stderr.write("%s:%s\n" % (Exception, ex))
            return 1
        for data in usr_data:
            if not(data['word'] in word_dict):
                word_list.append([data['word'], 100])
            if not(data['name'] in word_dict):
                word_list.append([data['name'], 100])
    '''
    global segger
    try:
        if not common_segment.seg_initial_list(word_list, segger):
            logger.info("initial segment done")
        else:
            logger.info("initial segment error")
            return 1
    except Exception,ex:
        logger.info("%s, %s" % (Exception, ex))
        return 1

    '''
    global match_dict
    try:
        'initial from file'
        #match_dict = match_keyword_bigram.match_bi_initial(conp_word_file)
        'initial from bin file'
        match_dict = match_bi_initial_bin(conp_word_file_bin)
        if None != match_dict:
            logger.info("initial match_keyword bin done")
        else:
            logger.info("initial match_keyword bin error")
            return 1

    except:
        logger.info("initial match_keyword error")
        return 1
    '''
    '''
    if topic_kw_table != '' and topic_name_table != '':
        match_dict = match_bi_initial_db(topic_kw_table, topic_name_table, match_dict)
        logger.info("initial match_keyword db")
    '''
    logger.info("initial done\n")
    return 0

#def is_stockinfo(txt, need_seg = 1):
def is_stockinfo(input_jstr):
    '判断是否是股评新闻'
    global bad_class_data
    global stock_thresh
    global segger
    input_data = json.loads(input_jstr)
    txt = input_data['txt']
    need_seg = 1
    if 'need_seg' in input_data:
        need_seg = input_data['need_seg']

    jstr = json.dumps({'message':None, 'stat':1})
    'check length'
    if len(txt) == 0:
        return jstr

    '''
    '大写转小写'
    txt = txt.lower()
    '''

    'seg'
    if 1 == need_seg:
        seg_list = common_segment.segment(txt, segger)
        if None == seg_list:
            return jstr
    else:
        seg_list = txt.split(' ')

    'to vector'
    vec_dict = txt2vec(seg_list)
    if None == vec_dict:
        return jstr

    'sim vs stock news'
    bad_sim_res = txt_sim(vec_dict, bad_class_data, 1.0, 1.0)
    if None == bad_sim_res:
        return jstr
    if len(bad_sim_res) == 1 and bad_sim_res[0]['sim'] >= stock_thresh:
        jstr = json.dumps({'message':{'is_stockinfo':True}, 'stat':0})
        return jstr
    jstr = json.dumps({'message':{'is_stockinfo':False}, 'stat':0})
    return jstr

def txt_topic(txt, t = -1, s = -1, need_seg = 1):
    global bad_class_data
    global class_data
    global match_dict
    global sim_thresh
    global stock_thresh
    global segger

    if t > 0:
        sim_thresh = t
    if s > 0:
        stock_thresh = s
    'check length'
    if len(txt) == 0:
        return []

    '''
    '大写转小写'
    txt = txt.lower()
    '''

    'seg'
    if 1 == need_seg:
        seg_list = common_segment.segment(txt, segger)
        if None == seg_list:
            return None
    else:
        #seg_list = txt.split(' ')
        seg_list = txt.split(' ')

    'to vector'
    # 使用title+全文生成的向量
    vec_dict = txt2vec(seg_list)
    # 使用title生成的向量
    head_vec_dict1 = txt2vec(seg_list, 1)
    # 使用title+第一段生成的向量
    head_vec_dict2 = txt2vec(seg_list, 2)
    if vec_dict is None or head_vec_dict1 is None or head_vec_dict2 is None:
        return None
    '''
    for k in vec_dict:
        sys.stdout.write("%s:%f " % (k.encode('utf-8'), vec_dict[k]))
    print ''
    '''

    '''
    'sim vs stock news'
    bad_sim_res = txt_sim(vec_dict, bad_class_data, 1.0, 1.0)
    if None == bad_sim_res:
        return None
    if len(bad_sim_res) == 1 and bad_sim_res[0]['sim'] >= stock_thresh:
        return []
    '''

    topic_sim = []
    topic_sim_dict = {}
    'sim of topics'
    #sim_res = txt_sim(vec_dict, class_data, 1.0, 1.0)
    #def txt_sim(txt_vec, class_vec_data, len1=0, len2=0):
    sim_res = []
    class_vec = class_data['vec']
    class_vlen = class_data['vlen']
    class_name = class_data['name']
    class_head_flag = class_data['head_flag']
    #if None == txt_vec or len(txt_vec) == 0:
    #    return None
    for m in range(0, len(class_vec)):
        #print class_vlen[m], 1.0
        if class_head_flag[m] == 0:
            sim = cosine_txt(class_vec[m], vec_dict, class_vlen[m], 1.0)
        elif class_head_flag[m] == 1:
            sim = cosine_txt(class_vec[m], head_vec_dict1, class_vlen[m], 1.0)
        else:
            sim = cosine_txt(class_vec[m], head_vec_dict2, class_vlen[m], 1.0)
        sim_res.append({'name':class_name[m], 'sim':sim})
    '''
    print sim_res
    '''

    if not sim_res:
        return None
    for data in sim_res:
        #print data['name']#.encode('utf-8')
        #print data['sim']
        #print(('%s\t%f' % (data['name'], data['sim'])).encode('utf-8'))
        if data['sim'] > sim_thresh:
            if data['name'] in topic_sim_dict and data['sim'] > topic_sim_dict[data['name']]:
                topic_sim_dict[data['name']] = data['sim']
            elif not(data['name'] in topic_sim_dict):
                topic_sim_dict[data['name']] = data['sim']

    '''
    'match keywords'
    match_res = None
    if match_dict != {}:
        match_res = match_bi_keyword(seg_list, match_dict, 'sim')
    if None == match_res:
        for tp in topic_sim_dict:
            topic_sim.append({'name':tp, 'sim':topic_sim_dict[tp]})
        return topic_sim
    for data in match_res:
        if data['sim'] > sim_thresh:
            if data['name'] in topic_sim_dict and data['sim'] > topic_sim_dict[data['name']]:
                topic_sim_dict[data['name']] = data['sim']
            elif not(data['name'] in topic_sim_dict):
                topic_sim_dict[data['name']] = data['sim']
    '''
    sim_sort = sorted(topic_sim_dict.iteritems(), key=lambda d:d[1], reverse=True)
    for da in sim_sort:
        topic_sim.append({'name':da[0], 'sim':da[1]})
    return topic_sim



"""
txt_sim.py
"""
def cosine(vec1, vec2, len1=0, len2=0):
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

def load_class(ifilename):
    'class vector file'
    try:
        ifile1 = open(ifilename)
    except:
        s = "open class_vec file: %s fail. %s line:[%d]\n" % (ifilename, __file__, sys._getframe().f_lineno)
        sys.stderr.write(s)
        return None

    class_vec = []
    class_vlen = []
    class_name = []
    while 1:
        lines = ifile1.readlines()
        if not lines:
            break
        for line in lines:
            line = line.rstrip('\n')
            line = line.decode('utf-8')
            tab_list = line.split('\t')
            class_name.append(tab_list[0])
            tmp_list = []
            sum = 0
            for i in range(1,len(tab_list),2):
                tmp_list.append([int(tab_list[i]), float(tab_list[i+1])])
                sum += math.pow(float(tab_list[i+1]), 2)
            sum = math.sqrt(sum)
            class_vec.append(tmp_list)
            class_vlen.append(sum)
    ifile1.close()
    class_data = {'vec':class_vec, 'vlen':class_vlen, 'name':class_name}
    return class_data

def load_class_bin(vec_file_bin):
    'class vector file'
    #vec_dict = bin_util.load_vec(vec_on_file_bin)
    vec_dict = common_bin_util.load_txt_vec(vec_file_bin)
    if None == vec_dict:
        s = "read class_vec file: %s fail. %s line:[%d]\n" % (vec_file_bin, __file__, sys._getframe().f_lineno)
        sys.stderr.write(s)
        return None
    class_vec = []
    class_vlen = []
    class_name = []
    for vname in vec_dict:
        vec = vec_dict[vname]
        new_vec = {}
        for k in vec:
            new_vec[k.decode('utf-8')] = vec[k]
        class_vec.append(new_vec)
        #class_name.append(vname.decode('utf-8'))
        class_name.append(vname)
        sum = 0
        for fea in vec:
            sum += math.pow(vec[fea], 2)
        sum = math.sqrt(sum)
        class_vlen.append(sum)
    class_data = {'vec':class_vec, 'vlen':class_vlen, 'name':class_name}
    return class_data

def txt_sim_id(txt_vec, class_vec_data):
    sim_res = []
    class_vec = class_vec_data['vec']
    class_vlen = class_vec_data['vlen']
    class_name = class_vec_data['name']
    if None == txt_vec or len(txt_vec) == 0:
        return None
    for m in range(0, len(class_vec)):
        sim = cosine(class_vec[m], txt_vec, class_vlen[m], 0)
        sim_res.append({'name':class_name[m], 'sim':sim})
    return sim_res

def txt_sim(txt_vec, class_vec_data, len1=0, len2=0):
    sim_res = []
    class_vec = class_vec_data['vec']
    class_vlen = class_vec_data['vlen']
    class_name = class_vec_data['name']
    if None == txt_vec or len(txt_vec) == 0:
        return None
    for m in range(0, len(class_vec)):
        #print class_vlen[m], 1.0
        sim = cosine_txt(class_vec[m], txt_vec, class_vlen[m], 1.0)
        sim_res.append({'name':class_name[m], 'sim':sim})
    return sim_res

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


"""
txt2vec.py
#worddict = '/home/andy/hot_topic/data/word_dict.2'
"""
def load_worddict(worddict):
    global word_dict
    try:
        ifile = open(worddict)
    except:
        sys.stderr.write("open worddict[%s] error\n" % worddict)
        return 1
    while 1:
        lines = ifile.readlines()
        if not lines:
            break
        for line in lines:
            line = line.rstrip('\n')
            tablist = line.split('\t')
            #word_dict[tablist[0].encode('utf-8')] = int(tablist[1])
            word_dict[tablist[0].decode('utf-8')] = int(tablist[1])
    ifile.close()
    return 0

def load_worddict_bin(worddict):
    global word_dict
    word_list = common_bin_util.load_word_dict(worddict)
    if None == word_list:
        return 1
    for data in word_list:
        w = data[0].decode('utf-8')
        i = data[1]
        word_dict[w] = i
    return 0

def txt2vec_id(term_list):
    global word_dict
    vec_list = []
    tmp_dict = {}
    tf_sum = 0
    if None == term_list:
        return None
#    print word_dict[u'管道']
    for term in term_list:
        #if term.encode('utf-8') in word_dict:
        if term in word_dict:
#            print term
            wid = word_dict[term]
            if not(wid in tmp_dict):
                tmp_dict[wid] = 0
            tmp_dict[wid] += 1.0
            tf_sum += 1.0

    tmp_sort = sorted(tmp_dict.iteritems(), key=lambda d:d[0])
    for data in tmp_sort:
        '[wordid, fea_value]'
        vec_list.append([data[0], data[1]/tf_sum])
    return vec_list

def txt2vec(term_list, head_flag=0):
    # head_flag:是否只使用title和第一段,1:yes,0:no
    #返回一个dict,{fea_txt:weight, ...}
    print_flag = 0
    global vocabulary
    vec_dict = {}
    tmp_dict = {}
    tf_sum = 0.0
    if None == term_list:
        return None
    endline_cnt = 0
    for term in term_list:
        if print_flag == 1:
            print term.encode('utf-8')
        if term == '#&#':
            endline_cnt += 1
        if head_flag == 1 and endline_cnt == 1:
            break
        if head_flag == 2 and endline_cnt == 2:
            break
        if term not in vocabulary:
            continue
        if len(term)>1 and not(p_term.match(term)):
            if not(term in tmp_dict):
                tmp_dict[term] = 0
            tmp_dict[term] += 1.0

    for term in tmp_dict:
        tf_sum += tmp_dict[term] * tmp_dict[term]
    tf_sum = math.sqrt(tf_sum)
    for term in tmp_dict:
        tmp_dict[term] = tmp_dict[term] / tf_sum
    if print_flag == 1:
        for w in tmp_dict:
            print(('%s\t%f' % (w, tmp_dict[w])).encode('utf-8'))
    return tmp_dict


def load_vocabulary(vocabulary_file):
    # 加载用于向量化的词典
    vocabulary = {}
    vfile = open(vocabulary_file)
    for line in vfile.readlines():
        line = line.decode('utf-8')
        line = line.rstrip('\n')
        tlist = line.split('\t')
        vocabulary[tlist[0]] = int(tlist[1])
    vfile.close()
    return vocabulary


"""
match_keyword_bigram.py
"""
def word_doc2(word_list, word_dict):
    '用二元关键词词典统计出现关键词的段落数'
    para_cnt_dict = {}
    sen_cnt_dict = {}
    word_cnt_dict = {}
    para_flag_dict = {}
    sen_flag_dict = {}

    term_list = []
    term_idx = 0
    valid_length = 30

    #para_list = doc.split('#&#')
    #print "para count: " + str(len(para_list))

    return_list = [para_cnt_dict, sen_cnt_dict, word_cnt_dict]
    sen_end_dict = {u'。':1, u'！':1, u'？':1, u'……':1}
    para_idx = 0
    sen_idx = 0
    title_weight = 1
    para_len = 0
    sen_len = 0

    for term in word_list:
        #print term.encode('utf-8')
        if term == '#&#' or term == '\n':
            para_idx += 1
            para_flag_dict = {}
            para_len = 0
            if sen_len > 5:
                sen_idx += 1
            sen_flag_dict = {}
            sen_len = 0
            continue
        elif term in sen_end_dict:
            sen_idx += 1
            sen_flag_dict = {}
            sen_len = 0
            continue
        elif term in word_dict:
            term_list.append({'term':term, 'term_idx':term_idx, 'sen_idx':sen_idx, 'para_idx':para_idx})
            sub_dict = word_dict[term]
            if len(sub_dict) == 1 and term in sub_dict:
                '非二元关键词'
                stop_idx = len(term_list) - 2
            else:
                stop_idx = -1
            for i in range(len(term_list) - 1, stop_idx, -1):
                #print term.encode('utf-8')
                #print term_list
                #print i
                #print stop_idx
                if i != len(term_list) - 1 and term_list[i]['term'] == term:
                    '和当前term一样的term，避免重复计算'
                    break
                if term_list[i]['term'] in sub_dict and term_list[i]['para_idx'] == para_idx and term_idx - term_list[i]['term_idx'] <= valid_length:
                    '有效范围是和当前term在同一自然段，距离小于等于valid_length个term'
                    bi_term = term + "@+@" + term_list[i]['term']
                    #print bi_term.encode('utf-8')
                    if bi_term in word_cnt_dict:
                        word_cnt_dict[bi_term] += 1
                    else:
                        word_cnt_dict[bi_term] = 1

                    if not (bi_term in para_flag_dict):
                        if bi_term in para_cnt_dict:
                            para_cnt_dict[bi_term] += 1
                        else:
                            if para_idx == 0:
                                para_cnt_dict[bi_term] = 1 * title_weight
                            else:
                                para_cnt_dict[bi_term] = 1
                        para_flag_dict[bi_term] = 1

                    if not (bi_term in sen_flag_dict):
                        if bi_term in sen_cnt_dict:
                            sen_cnt_dict[bi_term] += 1
                        else:
                            sen_cnt_dict[bi_term] = 1
                        sen_flag_dict[bi_term] = 1
                if term_list[i]['para_idx'] != para_idx or term_idx - term_list[i]['term_idx'] > valid_length:
                    '超过了有效范围'
                    break
        term_idx += 1
        para_len += 1
        sen_len += 1
    if para_len > 10:
        para_idx += 1
    if sen_len > 5:
        sen_idx += 1
    sen_cnt_dict[' '] = sen_idx
    para_cnt_dict[' '] = para_idx
    return return_list

def word2conp(conp_dict, word_list):
    para_dict = word_list[0]
    sen_dict = word_list[1]
    tf_dict = word_list[2]
    conp_para_dict = {}
    conp_sen_dict = {}
    conp_tf_dict = {}
    return_list = [conp_para_dict, conp_sen_dict, conp_tf_dict]
    for w in para_dict:
        if w in conp_dict:
            for c in conp_dict[w]:
                if c in conp_para_dict:
                    conp_para_dict[c] += para_dict[w]
                else:
                    conp_para_dict[c] = para_dict[w]
    for w in sen_dict:
        if w in conp_dict:
            for c in conp_dict[w]:
                if c in conp_sen_dict:
                    conp_sen_dict[c] += sen_dict[w]
                else:
                    conp_sen_dict[c] = sen_dict[w]
    for w in tf_dict:
        if w in conp_dict:
            for c in conp_dict[w]:
                if c in conp_tf_dict:
                    conp_tf_dict[c] += tf_dict[w]
                else:
                    conp_tf_dict[c] = tf_dict[w]

    return return_list

def match_bi_initial(dict_file):
    '二元概念关键字'
    try:
        wfile = open(dict_file)
    except:
        sys.stderr.write("open conp_word_file[%s] error\n" % dict_file)
        return None
    word_dict = {}
    bigram_dict = {}
    while 1:
        lines = wfile.readlines()
        if not lines:
            break
        for line in lines:
            line = line.rstrip('\n')
            line = line.rstrip('\r')
            line = line.decode('utf-8')
            wlist = line.split('\t')
            for i in range(2, 2 + int(wlist[1])):
                terms = wlist[i].split("@+@")
                for j in range(0, len(terms)):
                    if not(terms[j] in word_dict):
                        word_dict[terms[j]] = {}
                    for k in range(0, len(terms)):
                        if len(terms) > 1 and j == k:
                            continue
                        if not(terms[k] in word_dict[terms[j]]):
                            word_dict[terms[j]][terms[k]] = []
                        word_dict[terms[j]][terms[k]].append(wlist[0])
                        bigram = terms[j] + "@+@" + terms[k]
                        if not(bigram in bigram_dict):
                            bigram_dict[bigram] = []
                        bigram_dict[bigram].append(wlist[0])
    wfile.close()
    return {'conp_dict':bigram_dict, 'word_dict':word_dict}

def match_bi_initial_mongo(coll):
    '二元概念关键字'
    word_dict = {}
    bigram_dict = {}
    for data in coll.find({}):
        wlist = data['dict']
        tp = data['w']
        for i in range(0, len(wlist)):
            terms = wlist[i].split("@+@")
            for j in range(0, len(terms)):
                if not(terms[j] in word_dict):
                    word_dict[terms[j]] = {}
                for k in range(0, len(terms)):
                    if len(terms) > 1 and j == k:
                        continue
                    if not(terms[k] in word_dict[terms[j]]):
                        word_dict[terms[j]][terms[k]] = []
                    word_dict[terms[j]][terms[k]].append(tp)
                    bigram = terms[j] + "@+@" + terms[k]
                    if not(bigram in bigram_dict):
                        bigram_dict[bigram] = []
                    bigram_dict[bigram].append(tp)
    return {'conp_dict':bigram_dict, 'word_dict':word_dict}

def match_bi_initial_bin(dict_file):
    '从二进制数据文件中读取二元概念关键字'
    try:
        bf = open(dict_file, 'rb')
    except:
        sys.stderr.write("open conp_word_file[%s] error\n" % dict_file)
        return None
    word_dict = {}
    bigram_dict = {}
    c = common_bin_util.load_string(bf)
    if None == c:
        return None
    while c != '' and c != None:
        c = c.decode('utf-8')
        wlist = []
        wlist.append(c)
        w_cnt = common_bin_util.load_num(bf, 'int')
        if None == w_cnt:
            return None
        wlist.append(str(w_cnt))
        for i in range(0, w_cnt):
            w = common_bin_util.load_string(bf)
            if None == w:
                return None
            w = w.decode('utf-8')
            wlist.append(w)
        for i in range(2, 2 + int(wlist[1])):
            terms = wlist[i].split("@+@")
            for j in range(0, len(terms)):
                if not(terms[j] in word_dict):
                    word_dict[terms[j]] = {}
                for k in range(0, len(terms)):
                    if len(terms) > 1 and j == k:
                        continue
                    if not(terms[k] in word_dict[terms[j]]):
                        word_dict[terms[j]][terms[k]] = []
                    word_dict[terms[j]][terms[k]].append(wlist[0])
                    bigram = terms[j] + "@+@" + terms[k]
                    if not(bigram in bigram_dict):
                        bigram_dict[bigram] = []
                    bigram_dict[bigram].append(wlist[0])
        c = common_bin_util.load_string(bf)
    bf.close()
    return {'conp_dict':bigram_dict, 'word_dict':word_dict}

'''
def match_bi_initial_db(topic_kw_table, topic_name_table, match_dict = {}):
    '从mongo中读取二元概念关键字, 加入到现有dict中'
    if len(match_dict) != 0:
        word_dict = match_dict['word_dict']
        bigram_dict = match_dict['conp_dict']
    else:
        word_dict = {}
        bigram_dict = {}

    try:
        dao = CommDao(topic_kw_table)
        kw_data = dao.find_all()
    except Exception, ex:
        sys.stderr.write("%s:%s\n" % (Exception, ex))
        return match_dict
    
    try:
        dao = CommDao(topic_name_table)
        tp_name_data = dao.find_all()
    except Exception, ex:
        sys.stderr.write("%s:%s\n" % (Exception, ex))
        return match_dict
    tp_name_dict = {}
    for data in tp_name_data:
        tp_name_dict[str(data['id'])] = data['name']
    tp_kw_dict = {}
    for data in kw_data:
        tp_id = data['concept_id']
        if tp_id in tp_name_dict:
            tp_name = tp_name_dict[tp_id]
            if not(tp_name) in tp_kw_dict:
                tp_kw_dict[tp_name] = []
            tp_kw_dict[tp_name].append(data['word'])
    
    for tp in tp_kw_dict:
        wlist = tp_kw_dict[tp]
        if wlist is None or tp is None:
            continue
        wlist.append(tp)
        for i in range(0, len(wlist)):
            terms = wlist[i].split("@+@")
            for j in range(0, len(terms)):
                if not(terms[j] in word_dict):
                    word_dict[terms[j]] = {}
                for k in range(0, len(terms)):
                    if len(terms) > 1 and j == k:
                        continue
                    if not(terms[k] in word_dict[terms[j]]):
                        word_dict[terms[j]][terms[k]] = []
                    for c in word_dict[terms[j]][terms[k]]:
                        if c == tp:
                            break
                    else:
                        word_dict[terms[j]][terms[k]].append(tp)
                    bigram = terms[j] + "@+@" + terms[k]
                    if not(bigram in bigram_dict):
                        bigram_dict[bigram] = []
                    for c in bigram_dict[bigram]:
                        if c == tp:
                            break
                    else:
                        bigram_dict[bigram].append(tp)
    return {'conp_dict':bigram_dict, 'word_dict':word_dict}
'''

'''
def match_bi_initial_mongo_add(coll, match_dict = {}):
    '从mongo中读取二元概念关键字, 加入到现有dict中'
    word_dict = match_dict['word_dict']
    bigram_dict = match_dict['conp_dict']
    try:
        coll.find_one({})
    except:
        sys.stderr.write("load form db error\n")
        return None
    for data in coll.find({}):
        wlist = data['dict']
        tp = data['w']
        for i in range(0, len(wlist)):
            terms = wlist[i].split("@+@")
            for j in range(0, len(terms)):
                if not(terms[j] in word_dict):
                    word_dict[terms[j]] = {}
                for k in range(0, len(terms)):
                    if len(terms) > 1 and j == k:
                        continue
                    if not(terms[k] in word_dict[terms[j]]):
                        word_dict[terms[j]][terms[k]] = []
                    for c in word_dict[terms[j]][terms[k]]:
                        if c == tp:
                            break
                    else:
                        word_dict[terms[j]][terms[k]].append(tp)
                    bigram = terms[j] + "@+@" + terms[k]
                    if not(bigram in bigram_dict):
                        bigram_dict[bigram] = []
                    for c in bigram_dict[bigram]:
                        if c == tp:
                            break
                    else:
                        bigram_dict[bigram].append(tp)
    return {'conp_dict':bigram_dict, 'word_dict':word_dict}
'''

def write_match_bi_bin(txt_file, bin_file):
    '把二元概念关键字写入到二进制文件中'
    try:
        tf = open(txt_file)
    except:
        sys.stderr.write("open conp_word_file[%s] error\n" % txt_file)
        return 1
    try:
        bf = open(bin_file, 'wb')
    except:
        sys.stderr.write("open conp_word_file[%s] error\n" % bin_file)
        return 1
    while 1:
        lines = tf.readlines()
        if not lines:
            break
        for line in lines:
            line = line.rstrip('\n')
            line = line.rstrip('\r')
            #line = line.decode('utf-8')
            wlist = line.split('\t')
            common_bin_util.write_string(wlist[0], bf)
            common_bin_util.write_num(len(wlist)-2, bf, 'int')
            for i in range(2, len(wlist)):
                common_bin_util.write_string(wlist[i], bf)
    bf.close()
    tf.close()
    return 0

def match_bi_keyword(term_list, match_dict, method = 'sim'):
    if None == term_list or len(term_list) == 0:
        return None
    if not('word_dict' in match_dict) or not('conp_dict' in match_dict):
        return None
    word_dict = match_dict['word_dict']
    conp_dict = match_dict['conp_dict']
    para_cnt_thresh = 3
    match_res = []

    fre_list = word_doc2(term_list, word_dict)
    para_fre_dict = fre_list[0]
    sen_fre_dict = fre_list[1]

    debug_flag = 0
    if debug_flag:
        print ' '.join(fre_list[0].keys()).encode('utf-8')
        print fre_list[0].values()
        print ' '.join(fre_list[1].keys()).encode('utf-8')
        print fre_list[1].values()
        print ' '.join(fre_list[2].keys()).encode('utf-8')
        print fre_list[2].values()

    #conp_fre_list = word2conp(word_dict, fre_list)
    conp_fre_list = word2conp(conp_dict, fre_list)
    if debug_flag:
        print ' '.join(conp_fre_list[0].keys()).encode('utf-8')
        print conp_fre_list[0].values()
        print ' '.join(conp_fre_list[1].keys()).encode('utf-8')
        print conp_fre_list[1].values()
        print ' '.join(conp_fre_list[2].keys()).encode('utf-8')
        print conp_fre_list[2].values()

    para_cnt = fre_list[0][' ']
    if para_cnt == 0:
        para_cnt = 1
    sen_cnt = fre_list[1][' ']
    if sen_cnt == 0:
        sen_cnt = 1
    conp_para_dict = conp_fre_list[0]
    conp_sen_dict = conp_fre_list[1]
    for c in conp_para_dict:
        if method == 'sim':
            para_ratio = 1.0*conp_para_dict[c]/para_cnt
            sen_ratio = 1.0*conp_sen_dict[c]/sen_cnt
            sim = para_ratio * 0.5 + sen_ratio * 0.5
            if debug_flag:
                print 1.0*conp_para_dict[c]/para_cnt
                print conp_sen_dict[c]
                print sen_ratio
            #if (1.0*conp_para_dict[c]/para_cnt >0.25) and (conp_sen_dict[c] > 1 or sen_ratio >= 0.5):
            if (1.0*conp_para_dict[c]/para_cnt >0.25 or conp_para_dict[c] >= para_cnt_thresh) and (conp_sen_dict[c] > 1 or sen_ratio >= 0.5):
                if sim > 0.5:
                    #sim = sim / 2
                    sim = sim / (sim + 1)
                match_res.append({'name':c, 'sim':sim})
        elif method == 'match':
            if conp_fre_list[2][c] > 0:
                match_res.append({'name':c, 'count':conp_fre_list[2][c]})


        '''
        print ' '.join(conp_fre_list[0].keys())
        print conp_fre_list[0].values()
        print ' '.join(conp_fre_list[1].keys())
        print conp_fre_list[1].values()
        print ' '.join(conp_fre_list[2].keys())
        print conp_fre_list[2].values()
        '''
    return match_res



class Worker:

    def __init__(self, parameter):
        '构造函数'
        # parameter:初始化参数
        # parameter={'base_path':资源路径(相对路径,必有), 'model_path':模型路径(相对路径,必有), 'vocabulary':用于向量化的词典必有, 'seg_table':'实体词表,可选', 'topic_kw_table':概念相关词表,可选, 'topic_name_table':概念名称表,可选}

        self.initialed = 0
        if topic_initial(parameter):
            sys.stderr.write('initial error\n')
        else:
            sys.stderr.write('initial success\n')
            self.initialed = 1

    # [{u'list': [{u'name': u'\u623f\u5730\u4ea7', u'sim': 0.49663526244952894}]}, {u'list': []}]
    def process(self, parameter):
        '返回多篇新闻提取概念的结果'
        # 要求输入的新闻文本utf8编码, 以"#&#"或"\n"换行},]
        # parameter=[{'data':{'title':title必有可为空不可为None, 'content':content必有可为空不可为None}, config':{'t':sim_thresh可选, 's':stock_thresh可选}},]
        # return:
        # 处理成功:
        # {'message':[[{'name':概念名称, 'sim':相关度float},],], 'stat':0}
        # 处理失败:
        # {'message':None, 'stat':1}
        result_list = []
        global sim_thresh
        global stock_thresh
        if not self.initialed:
            return json.dumps({'message':None, 'stat':1})
        input_data = json.loads(parameter)
        for data_i in input_data:
            data = data_i['data']
            para = data_i['config'] if 'config' in data_i and data_i['config'] else {}
            if 't' in para and para['t'] != None:
                sim_t = para['t']
            else:
                sim_t = sim_thresh
            if 's' in para and para['s'] != None:
                stock_t = para['s']
            else:
                stock_t = stock_thresh
            if not('title' in data) or not('content' in data):
                sys.stderr.write("need title and content\n")
                result_list.append({"list": []})
                continue
            res = txt_topic(data['title'] + '#&#' + data['content'], sim_t, stock_t)
            result_list.append({"list": res})

        '''
        for txt in input_data:
            res = txt_topic(txt['content'])
            result_list.append({"list": res})
        '''
        return json.dumps({'message':result_list, 'stat': 0})


    def validate(self, input_jstr):
        '测试模型'
        # parameter=[{'data':{'title':title必有可为空不可为None, 'content':content必有可为空不可为None, 'conp':[conp,]必有可为空不可谓None}, config':{'t':sim_thresh可选, 's':stock_thresh可选}},]
        # return:
        # 处理成功:
        # {'message':{'accu':准确率float, 'rec':召回率float, 'f':F值float}, 'stat':0}
        # 处理失败:
        # {'message':None, 'stat':1}
        input_data = json.loads(input_jstr)
        global sim_thresh
        global stock_thresh
        if not self.initialed:
            return json.dumps({'message':None, 'stat':1})

        tag_cnt = 0 #标准答案数量, 按conp计算
        res_cnt = 0 #算法提取概念数量
        right_cnt = 0 #算法提取概念正确数量
        para = input_data['config']
        for data in input_data['data']:
            if 't' in para and para['t'] != None:
                sim_t = para['t']
            else:
                sim_t = sim_thresh
            if 's' in para and para['s'] != None:
                stock_t = para['s']
            else:
                stock_t = stock_thresh
            conp_list = data['conp']
            tag_cnt += len(conp_list)
            #print conp_list
            #print tag_cnt
            if not('title' in data) or not('content' in data):
                sys.stderr.write("need title and content\n")
                return json.dumps({'message':None, 'stat':1})
            #print data['content'].encode('utf-8')
            res = txt_topic(data['title'] + '#&#' + data['content'], sim_t, stock_t)
            if res is None:
                continue
            print "res:", res, 'conp_list:', conp_list, 'txt:', data['content'].encode('utf-8')
            for res_data in res:
                name = res_data['name']
                for conp in conp_list:
                    if conp == name:
                        right_cnt += 1
                        break
            res_cnt += len(res)
        if res_cnt == 0:
            accu = 0
        else:
            accu = float(right_cnt) / res_cnt
        if tag_cnt == 0:
            rec = 0
        else:
            rec = float(right_cnt) / tag_cnt
        if right_cnt == 0:
            f = 0.0
        else:
            f = 2 * accu * rec / (accu + rec)
        res = {'message':{'accu':accu, 'rec':rec, 'f':f, 'tag_cnt':tag_cnt, 'right_cnt':right_cnt}, 'stat':0}
        res_jstr = json.dumps(res)
        return res_jstr


def test():
    conf_data = {}
    conf_data['base_path'] = '../config/match_concept/base_data'
    conf_data['model_path'] = '../config/match_concept/model'
    conf_data['db_jar_file'] = '../lib/jar/data-access-service-all-0.0.1.jar'
    #conf_data['sim_thresh'] = 0.1
    #conf_data['stock_thresh'] = 0.15

    conf_data['topic_kw_table'] = 'csf_corpus.nlp_dict_concept_word'
    conf_data['topic_name_table'] = 'csf_corpus.nlp_dict_concept_base'
    conf_data['seg_table'] = 'csf_corpus.nlp_dict_entity'

    '''
    conf_data['seg_usr_dict_bin'] = 'jieba_user.dict.bin'
    conf_data['bad_class_vec_file_bin'] = 'badall.fea.f.bin'
    conf_data['class_vec_file_bin'] = 'all_text.id.rmbad.seg.match_r2.fea1.bin'
    conf_data['conp_word_file_bin'] = 'conp_words.all.bi.new.bin'
    conf_data['worddict_bin'] = 'word_dict.2.bin'
    conf_data['mongo_ip'] = '54.223.45.156'
    conf_data['mongo_port'] = 27017
    conf_data['mongo_slave'] = 1
    conf_data['mongo_db'] = 'graph'
    conf_data['mongo_coll'] = 'topic_dict'

    conf_data['log_path'] = './'
    conf_data['log_file'] = 'txt_topic.log'
    '''

    conf_jstr = json.dumps(conf_data)
    t_worker = Worker(conf_jstr)
    txt_list = []
    title_list = []
    input_list = []
    ifile = open(conf_data['base_path']+"/test.txt")
    while 1:
        lines = ifile.readlines()
        if not lines:
            break
        for line in lines:
            line = line.rstrip('\n')
            tablist = line.split('\t')
            txt_list.append({'content':tablist[1]})
            title_list.append(tablist[0])
            title = tablist[0]
            content = tablist[1]
            input_list.append({'data':{'title':title, 'content':content}, 'config':{'t':0.1, 's':0.15}})
    ifile.close()
    input_jstr = json.dumps(input_list)
    res_jstr = t_worker.process(input_jstr)
    print ("result:"), res_jstr

    res_data = json.loads(res_jstr)
    res_list = res_data['message']
    for i in range(0, len(title_list)):
        reses = res_data['message'][i]['list']
        s = title_list[i]
        tp = ''
        for res in reses:
            tp = tp + res['name'].encode('utf-8') + ':' + str(res['sim']).encode('utf-8') + '|'
        #print tp
        print "%s\t%s" % (tp, s)

def test_validate():
    conf_data = {}
    conf_data['base_path'] = '../config/match_concept/base_data'
    conf_data['model_path'] = '../config/match_concept/model'
    conf_data['db_jar_file'] = '../lib/jar/data-access-service-all-0.0.1.jar'
    #conf_data['sim_thresh'] = 0.1
    #conf_data['stock_thresh'] = 0.15

    conf_data['topic_kw_table'] = 'csf_corpus.nlp_dict_concept_word'
    conf_data['topic_name_table'] = 'csf_corpus.nlp_dict_concept_base'
    conf_data['seg_table'] = 'csf_corpus.nlp_dict_entity'

    conf_jstr = json.dumps(conf_data)
    t_worker = Worker(conf_jstr)
    txt_list = []
    title_list = []
    ifile = open(conf_data['base_path']+"/validate.test")
    input_list = []
    while 1:
        lines = ifile.readlines()
        if not lines:
            break
        for line in lines:
            line = line.rstrip('\n')
            tablist = line.split('\t')
            if tablist[0] != '':
                conp_list = tablist[0].split('|')
            else:
                conp_list = []
            title = tablist[1]
            content = tablist[2]
            input_list.append({'title':title, 'content':content, 'conp':conp_list})
            #title_list.append(tablist[0])
    ifile.close()
    input_data = {'data':input_list, 'config':{'t':0.1, 's':0.15}}
    input_jstr = json.dumps(input_data)
    res_jstr = t_worker.validate(input_jstr)
    res_data = json.loads(res_jstr)
    res_list = res_data['message']
    print (res_list)

if __name__ == '__main__':
    #test()
    test_validate()

