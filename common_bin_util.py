#!/usr/bin/python
#coding=utf8
"""
# Author: andy
# Created Time : 2017-04-06 11:30:16

# File Name: common_bin_util.py
# Description: 读写二进制词典文件

"""

import sys
import struct

INT_LEN = 4
CODE_STR = 'utf-16'

def load_jieba_dict(dict_file):
    '''
    读取结巴分词用户词典二进制文件
    文件格式:int,string,int
    第一个int:词的长度
    string:词
    第二个int:词频
    output:[[word(string), word_fre(int)],] word是utf8编码
    '''
    try:
        bf = open(dict_file, 'rb')
    except Exception,ex:
        sys.stderr.write("%s:%s\n" % (Exception, ex))
        return None
    global INT_LEN
    word_list = []
    b_read = bf.read(INT_LEN)
    while b_read != '':
        wlen = struct.unpack('i', b_read)[0]
        fmt = "%dsi" % (wlen)
        pack_len = struct.calcsize(fmt)
        u_p = struct.unpack(fmt, bf.read(pack_len))
        word = ((u_p[0]).decode(CODE_STR)).encode('utf-8')
        wfre = u_p[1]
        word_list.append([word, wfre])
        b_read = bf.read(INT_LEN)
    bf.close()

    return word_list

def write_jieba_dict(word_list, dict_file):
    '''
    写入结巴分词用户词典二进制文件
    文件格式:int,string,int
    第一个int:词的长度
    string:词
    第二个int:词频
    input:[[word(string), word_fre(int)],] word是utf8编码
    '''
    try:
        bf = open(dict_file, 'wb')
    except Exception,ex:
        sys.stderr.write("%s:%s\n" % (Exception, ex))
        return 1
    for data in word_list:
        word = (data[0].decode('utf-8')).encode(CODE_STR)
        wfre = data[1]
        w_len = len(word)
        fmt = "i%dsi" % (w_len)
        pack_len = struct.calcsize(fmt)
        #print fmt
        bf.write(struct.pack(fmt, w_len, word, wfre))
    bf.close()

    return 0

def test_jieba_dict():
    word_list = []
    ifile = open('../match_company/data/jieba_user.dict')
    while 1:
        lines = ifile.readlines()
        if not lines:
            break
        for line in lines:
            line = line.rstrip('\n')
            tlist = line.split(' ')
            word_list.append([tlist[0], int(tlist[1])])
    write_jieba_dict(word_list, '../match_company/data/jieba_user.dict.bin')
    load_list = load_jieba_dict('../match_company/data/jieba_user.dict.bin')
    for data in load_list:
        print "%s\t%d" % (data[0], data[1])


def load_word_dict(dict_file):
    '''
    读取词典
    文件格式:int,string,int
    第一个int:词的长度
    string:词
    第二个int:词的id
    output:[[word(string), word_id(int)],] word是utf8编码
    '''
    try:
        bf = open(dict_file, 'rb')
    except Exception,ex:
        sys.stderr.write("%s:%s\n" % (Exception, ex))
        return None
    global INT_LEN
    word_list = []
    b_read = bf.read(INT_LEN)
    while b_read != '':
        wlen = struct.unpack('i', b_read)[0]
        fmt = "%dsi" % (wlen)
        pack_len = struct.calcsize(fmt)
        u_p = struct.unpack(fmt, bf.read(pack_len))
        word = ((u_p[0]).decode(CODE_STR)).encode('utf-8')
        wid = u_p[1]
        word_list.append([word, wid])
        b_read = bf.read(INT_LEN)
    bf.close()

    return word_list

def write_word_dict(word_list, dict_file):
    '''
    写入词典
    文件格式:int,string,int
    第一个int:词的长度
    string:词
    第二个int:词的id
    input:[[word(string), word_id(int)],] word是utf8编码
    '''
    try:
        bf = open(dict_file, 'wb')
    except Exception,ex:
        sys.stderr.write("%s:%s\n" % (Exception, ex))
        return 1
    for data in word_list:
        word = (data[0].decode('utf-8')).encode(CODE_STR)
        wid = data[1]
        w_len = len(word)
        fmt = "i%dsi" % (w_len)
        pack_len = struct.calcsize(fmt)
        #print fmt
        bf.write(struct.pack(fmt, w_len, word, wid))
    bf.close()

    return 0

def test_word_dict():
    ifile = open('./data/word_dict.2')
    word_list = []
    while 1:
        lines = ifile.readlines()
        if not lines:
            break
        for line in lines:
            line = line.rstrip('\n')
            tablist = line.split('\t')
            word_list.append([tablist[0], int(tablist[1])])
    ifile.close()
    write_jieba_dict(word_list, './data/word_dict.2.bin')
    load_list = load_jieba_dict('./data/word_dict.2.bin')
    for data in load_list:
        print "%s\t%d" % (data[0], data[1])

def load_vec(vec_file):
    '''
    读取向量数据
    文件格式:int,int,string,int,float,int,float...
    第1个int:词的长度
    第2个int:向量元素的数量
    string:向量名称
    int,float:特征id,特征值
    output:{vec_name(string):[[feaid(int), fea_value(float)],]} vec_name是utf8编码
    '''
    try:
        bf = open(vec_file, 'rb')
    except Exception,ex:
        sys.stderr.write("%s:%s\n" % (Exception, ex))
        return None
    vec_dict = {}
    b_read = bf.read(struct.calcsize('ii'))
    while b_read != '':
        word_len, vec_len = struct.unpack('ii', b_read)
        fmt = "%ds" % (word_len)
        pack_len = struct.calcsize(fmt)
        try:
            u_p = struct.unpack(fmt, bf.read(pack_len))
        except Exception,ex:
            sys.stderr.write("%s:%s\n" % (Exception, ex))
            return vec_dict
        vec_name = ((u_p[0]).decode(CODE_STR)).encode('utf-8')
        vec = []
        for i in range(0, vec_len):
            fmt = "if"
            pack_len = struct.calcsize(fmt)
            try:
                fid, fval = struct.unpack(fmt, bf.read(pack_len))
            except Exception,ex:
                sys.stderr.write("%s:%s\n" % (Exception, ex))
                return vec_dict
            vec.append([fid, fval])
        vec_dict[vec_name] = vec
        b_read = bf.read(struct.calcsize('ii'))
    bf.close()

    return vec_dict

def write_vec(vec_dict, vec_file):
    '''
    写入向量数据
    文件格式:int,int,string,int,float,int,float...
    第1个int:词的长度
    第2个int:向量元素的数量
    string:向量名称
    int,float:特征id,特征值
    input:
    {vec_name(string):[[feaid(int), fea_value(float)],]} vec_name是utf8编码
    vec_file 向量文件
    '''
    try:
        bf = open(vec_file, 'wb')
    except Exception,ex:
        sys.stderr.write("%s:%s\n" % (Exception, ex))
        return 1
    for vec_name in vec_dict:
        vec = vec_dict[vec_name]
        vname = (vec_name.decode('utf-8')).encode(CODE_STR)
        vn_len = len(vname)
        vec_len = len(vec)
        fmt = "ii%ds" % (vn_len)
        bf.write(struct.pack(fmt, vn_len, vec_len, vname))
        for i in range(0, vec_len):
            fmt = 'if'
            bf.write(struct.pack(fmt, vec[i][0], vec[i][1]))
    bf.close()
    return 0

def test_vec():
    vec_dict = {}
    vname1 = '向量1'
    vname2 = '向量2'
    vec1 = [[1, 0.5], [3, 0.2234], [8, 0.98791]]
    vec2 = [[2, 0.125], [4, 0.833], [9, 0.732], [1, 0.2398]]
    vec_dict[vname1] = vec1
    vec_dict[vname2] = vec2
    write_vec(vec_dict, 'vec.bin')
    vec_load = load_vec('vec.bin')
    for vname in vec_load:
        print vname
        print vec_load[vname]

def test_vec2(vec_txt_file):
    vec_dict = {}
    tfile = open(vec_txt_file)
    while 1:
        lines = tfile.readlines()
        if not lines:
            break
        for line in lines:
            line = line.rstrip('\n')
            tablist = line.split('\t')
            vname = tablist[0]
            vec = []
            for i in range(1, len(tablist), 2):
                idx = int(tablist[i])
                val = float(tablist[i+1])
                vec.append([idx, val])
            vec_dict[vname] = vec

    write_vec(vec_dict, vec_txt_file + '.bin')
    vec_load = load_vec(vec_txt_file + '.bin')
    for vname in vec_load:
        print vname
        print vec_load[vname]


def load_string(bf):
    '''
    从二进制文件中读取一个字符串
    二进制文件中保存格式为 int, string
    int是string的长度, string是要读取的字符串
    input:
        bf:打开的二进制文件, 从当前位置开始读取
    return:
        None:有错误
        string:正常, utf8
    '''
    s = ''
    try:
        b_read = bf.read(struct.calcsize('i'))
        if b_read == '':
            return s
        slen = (struct.unpack('i', b_read))[0]
    except Exception,ex:
        sys.stderr.write("%s:%s\n" % (Exception, ex))
        return None
    fmt = "%ds" % (slen)
    pack_len = struct.calcsize(fmt)
    try:
        b_read = bf.read(pack_len)
        if b_read == '':
            return s
        s = (((struct.unpack(fmt, b_read))[0]).decode(CODE_STR)).encode('utf-8')
    except Exception,ex:
        sys.stderr.write("%s:%s\n" % (Exception, ex))
        return None
    return s

def write_string(string, bf):
    '''
    把一个字符串写入到二进制文件中
    二进制文件中保存格式为 int, string
    int是string的长度, string是要读取的字符串
    input:
        string:要写入的字符串, utf8
        bf:打开的二进制文件, 从当前位置开始写入
    return:
        1:有错误
        0:正常
    '''
    s = string.decode('utf-8').encode(CODE_STR)
    try:
        bf.write(struct.pack('i', len(s)))
        fmt = "%ds" % len(s)
        bf.write(struct.pack(fmt, s))
    except Exception,ex:
        sys.stderr.write("%s:%s\n" % (Exception, ex))
        return 1
    return 0

def test_string():
    slist = ['参股@+@基金', '汉语', '简体字', '普通话']
    bf = open('string.bin', 'wb')
    for s in slist:
        write_string(s, bf)
    bf.close()
    bf = open('string.bin', 'rb')
    s = load_string(bf)
    while s != '' and s != None:
        print s
        s = load_string(bf)

def load_num(bf, kind = 'int'):
    '''
    从二进制文件中读取一个数字
    input:
        bf:打开的二进制文件, 从当前位置开始读取
        kind:数字类型'int'/'float'
    return:
        None:有错误, 或文件已结束
        int:正常
    '''
    try:
        if kind == 'int':
            fmt = 'i'
        elif kind == 'float':
            fmt = 'f'
        b_read = bf.read(struct.calcsize(fmt))
        if b_read == '':
            return None
        i = (struct.unpack(fmt, b_read))[0]
    except Exception,ex:
        sys.stderr.write("%s:%s\n" % (Exception, ex))
        return None
    return i

def write_num(i, bf, kind = 'int'):
    '''
    把一个数字写入到二进制文件中
    input:
        int:要写入的数字
        bf:打开的二进制文件, 从当前位置开始写入
        kind:数字类型'int'/'float'
    return:
        1:有错误
        0:正常
    '''
    try:
        if kind == 'int':
            fmt = 'i'
        elif kind == 'float':
            fmt = 'f'
        bf.write(struct.pack(fmt, i))
    except Exception,ex:
        sys.stderr.write("%s:%s\n" % (Exception, ex))
        return 1
    return 0

def test_num():
    ilist = [2234.23, 497.987, 287.2987, 945]
    bf = open('int.bin', 'wb')
    kind = 'float'
    for i in ilist:
        write_num(i, bf, kind)
    bf.close()
    bf = open('int.bin', 'rb')
    i = load_num(bf, kind)
    while i != None:
        print i
        i = load_num(bf, kind)


def load_txt_vec(vec_file, utf8_flag = 1):
    '''
    读取向量数据
    文件格式:int,int,string,int,string,float,int,string,float...
    第1个int:向量元素的数量
    第2个int:vec_name的长度
    string:向量名称vec_name
    int,string,float:特征词长,特征,特征值
    output:{vec_name(string):[[fea(string), fea_value(float)],]}
    if utf8_flag==1:vec_name & fea是utf8编码;else:是unicode编码
    '''
    try:
        bf = open(vec_file, 'rb')
    except Exception,ex:
        sys.stderr.write("%s:%s\n" % (Exception, ex))
        return None
    vec_dict = {}
    b_read = bf.read(struct.calcsize('ii'))
    while b_read != '':
        vec_len, word_len = struct.unpack('ii', b_read)
        fmt = "%ds" % (word_len)
        pack_len = struct.calcsize(fmt)
        try:
            u_p = struct.unpack(fmt, bf.read(pack_len))
        except Exception,ex:
            sys.stderr.write("%s:%s\n" % (Exception, ex))
            return vec_dict
        if 1 == utf8_flag:
            vec_name = ((u_p[0]).decode(CODE_STR)).encode('utf-8')
        else:
            vec_name = (u_p[0]).decode(CODE_STR)
        vec = {}
        for i in range(0, vec_len):
            fea = load_string(bf)
            if 1 != utf8_flag:
                fea = fea.decode('utf-8')
            fval = load_num(bf, 'float')
            vec[fea] = fval
        vec_dict[vec_name] = vec
        b_read = bf.read(struct.calcsize('ii'))
    bf.close()
    return vec_dict

def write_txt_vec(vec_dict, vec_file):
    '''
    写入向量数据
    文件格式:int,int,string,int,string,float,int,string,float...
    第1个int:向量元素的数量
    第2个int:vec_name的长度
    string:向量名称vec_name
    int,string,float:词长,特征,特征值
    input:
    {vec_name(string):{fea(string):fea_value(float),...}, ...} vec_name是utf8编码
    vec_file 向量文件
    '''
    try:
        bf = open(vec_file, 'wb')
    except Exception,ex:
        sys.stderr.write("%s:%s\n" % (Exception, ex))
        return 1
    for vec_name in vec_dict:
        vec = vec_dict[vec_name]
        vec_len = len(vec)
        if write_num(vec_len, bf, 'int'):
            return 1
        if write_string(vec_name, bf):
            return 1
        for fea in vec:
            if write_string(fea, bf):
                return 1
            if write_num(vec[fea], bf, 'float'):
                return 1
    bf.close()
    return 0

def test_vec3(vec_file, write_flag=0):
    # 读取或写入二进制向量模型文件
    # input:
    # vec_file:向量文件, write_flag==0时，是二进制文件; write_flag==1时，是文本文件
    # output:
    # write_flag==0时，输出到stdout; write_flag==1时，输出到vec_file'.bin'
    if write_flag == 1:
        vec_dict = {}
        tfile = open(vec_file)
        while 1:
            lines = tfile.readlines()
            if not lines:
                break
            for line in lines:
                line = line.rstrip('\n')
                tablist = line.split('\t')
                vname = tablist[0]
                vec = {}
                for i in range(1, len(tablist), 2):
                    fea = tablist[i]
                    val = float(tablist[i+1])
                    vec[fea]=val
                vec_dict[vname] = vec

        write_txt_vec(vec_dict, vec_file + '.bin')
        vec_load = load_txt_vec(vec_file + '.bin')
    else:
        vec_load = load_txt_vec(vec_file)
        for vname in vec_load:
            s = vname
            for fea in vec_load[vname]:
                s = "%s\t%s\t%f" % (s, fea, vec_load[vname][fea])
            print s
        #print "%s\t%s" % (vname, str(vec_load[vname]))

if __name__ == '__main__':
    #test_jieba_dict()
    #test_word_dict()
    #test_vec()
    #test_vec2('./data/badall.fea.f')
    #test_vec2('./data/all_text.id.rmbad.seg.match_r2.fea1')
    #test_string()
    #test_num()
    #test_vec3('../data/fea_vec')
    #test_vec3('../model_path/001_10_50/conp_vec.bin')
    # argv[1]:input_file, argv[2]:write_flag(1/0)
    test_vec3(sys.argv[1], int(sys.argv[2]))

