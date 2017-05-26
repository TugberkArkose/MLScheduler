#!/bin/sh

#cd _bigLittle_hrrs_spec_tugberk_ml 
#printf "\nSPEC EXE TIMES\n "
#./getexetime.sh

#cd ../_bigLittle_hrrs_splash_tugberk_ml
#printf "\nSPLASH EXE TIMES\n "
#./getexetime.sh
#cd ../

printf "\nSPEC EXE TIMES\n "
for i in _bigLittle_hrrs_spec_tugberk_*
 do
  echo $i
  cd $i
  ./getexetime.sh
  cd ..
done
printf "\nSPLASH EXE TIMES\n "
for i in _bigLittle_hrrs_splash_tugberk_*
  do
  echo $i
  cd $i
  ./getexetime.sh
  cd ..
done

