#!/bin/bash

for i in combinations_spec_*
do
#cd _bigLittle_hrrs_spec_tugberk
cd $i
echo $i
if [ -z "$1" ] 
then
 rm -r cmp_*
 rm -r EightThreads_*
else
 mkdir $1
 mv cmp_* $1
 mv EightThreads_* $1
fi
cd run/
rm -r *.sh
python create.py
chmod +x *.sh
./torun_cpu_all_combination.sh
cd ../../
done
