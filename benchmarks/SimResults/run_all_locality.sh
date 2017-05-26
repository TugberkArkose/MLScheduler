#!/bin/bash

for i in _bigLittle*_locality
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
./torun_all.sh
cd ../../
done

