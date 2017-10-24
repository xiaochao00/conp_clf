#########################################################################
# File Name: metric.sh
# Author: andy
# mail: andy.jia@chinascope.com
# Created Time: 2017-10-19 10:18:17
#########################################################################
#!/bin/bash
# 检查结果的准确率和召回率

conp_name_file="../data/conp_name"
res_file="test.all.res"

while read name
do 
    awk -F"\t" -v c=$name 'BEGIN{tag=0;right=0;wrong=0;}{
        if($1~c){
            tag++;
            n=split($2,arr,"|");
            for(i=1;i<=n;i++){
                m=split(arr[i],val," ");
                if(val[1]==c)
                    right++;
            }
        }else if($2~c" ")
            wrong++;
        }END{
            print "----"c"----";
            print "tag:"tag"\tright:"right"\twrong:"wrong;
            if(right+wrong == 0)
                print "pre:0";
            else
                print "pre:"(0.0+right)/(right+wrong);
            if(tag == 0)
                print "rec:0";
            else
                print "rec:"(0.0+right)/tag;
        }' $res_file
done < $conp_name_file

