#!/usr/bin/python
#coding=utf8
"""
# Author: andy
# Created Time : 2017-10-14 14:25:04

# File Name: full2half.py
# Description:
全角数字英文转半角
"""
import sys

f2h_dict = {
u'０':'0',
u'１':'1',
u'２':'2',
u'３':'3',
u'４':'4',
u'５':'5',
u'６':'6',
u'７':'7',
u'８':'8',
u'９':'9',
u'ａ':'a',
u'ｂ':'b',
u'ｃ':'c',
u'ｄ':'d',
u'ｅ':'e',
u'ｆ':'f',
u'ｇ':'g',
u'ｈ':'h',
u'ｉ':'i',
u'ｊ':'j',
u'ｋ':'k',
u'ｌ':'l',
u'ｍ':'m',
u'ｎ':'n',
u'ｏ':'o',
u'ｐ':'p',
u'ｑ':'q',
u'ｒ':'r',
u'ｓ':'s',
u'ｔ':'t',
u'ｕ':'u',
u'ｖ':'v',
u'ｗ':'w',
u'ｘ':'x',
u'ｙ':'y',
u'ｚ':'z',
u'Ａ':'A',
u'Ｂ':'B',
u'Ｃ':'C',
u'Ｄ':'D',
u'Ｅ':'E',
u'Ｆ':'F',
u'Ｇ':'G',
u'Ｈ':'H',
u'Ｉ':'I',
u'Ｊ':'J',
u'Ｋ':'K',
u'Ｌ':'L',
u'Ｍ':'M',
u'Ｎ':'N',
u'Ｏ':'O',
u'Ｐ':'P',
u'Ｑ':'Q',
u'Ｒ':'R',
u'Ｓ':'S',
u'Ｔ':'T',
u'Ｕ':'U',
u'Ｖ':'V',
u'Ｗ':'W',
u'Ｘ':'X',
u'Ｙ':'Y',
u'Ｚ':'Z'}

def full2half(txt):
    # 全角数字英文转半角，输入为unicode编码
    if txt is None:
        return None
    char_list = list(txt)
    for i in range(len(char_list)):
        if char_list[i] in f2h_dict:
            char_list[i] = f2h_dict[char_list[i]]
    return ''.join(char_list)


if __name__ == '__main__':
    full_width = u' 很好aaｓｄｆｌｋｊ１２３４８７完成'
    half_width = full2half(full_width)
    print("full_width:%s" % full_width)
    print("half_width:%s" % half_width)

