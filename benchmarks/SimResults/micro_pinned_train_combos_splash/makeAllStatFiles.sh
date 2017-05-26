#!/bin/sh
# Job name
#$ -N pinnedfft
# Shell
#$ -S /bin/bash
#cd ..
#for directory in pinned*/; do
#  filename = "stats.out'"
 # target_filename="${directory}${filename}"
 # cd $directory
 # for i in stats*; do
  # echo $i
   #new="${directory//\//_}"
  # cp $i "${directory//\//_}${i}"
 # done
 # cd ..
#done


for i in cmp*/; do 
i=$(echo $i | tr '/' ' ')
echo $i
cd $i
#i = $( echo "$i" | tr ' ' '.')
#i = "${i// /_}"
echo $i
echo "${i}stats.out"
cp "stats.out" "${i}.stats" 
rename "s/ //g" *
cd ..; 
done
