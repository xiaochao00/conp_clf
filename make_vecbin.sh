#########################################################################
# File Name: make_vecbin.sh
# Author: andy
# mail: andy.jia@chinascope.com
# Created Time: 2017-10-12 22:06:21
#########################################################################
#!/bin/bash

python common_bin_util.py ../data/model_1vo/no_tid_10_50/conp_vec.bin0 0 >../data/model_1vo/no_tid_10_50/conp_vec.txt0
python common_bin_util.py ../data/model_1vo/no_tid_10_50/conp_vec.bin1 0 >../data/model_1vo/no_tid_10_50/conp_vec.txt1
cat ../data/model_1vo/no_tid_10_50/conp_vec.txt?* > ../data/model_1vo/no_tid_10_50/conp_vec.txt
python common_bin_util.py ../data/model_1vo/no_tid_10_50/conp_vec.txt 1
mv ../data/model_1vo/no_tid_10_50/conp_vec.txt.bin ../data/model_1vo/no_tid_10_50/conp_vec.bin

