#!/bin/bash
#for p in hrrs;
#do
#  echo $p;
#  for i in run ;
#  do
#    var=$(cat $p$i.o* | grep total   ) ;
#    echo $i $var;
#  done
#done

printf "\nSPEC IPC's\n "
for i in _bigLittle_hrrs_spec_tugberk_*
 do
  printf "\n"
  echo $i
  cd $i
  for p in cmp_ #EightThreads_
# pinned fair tlss hrrs;
  do
    echo $p;
    for j in perlbench bzip2 gcc bwaves gamess mcf milc zeusmp gromacs cactusADM leslie3d namd gobmk soplex povray calculix hmmer sjeng GemsFDTD libquantum h264ref tonto lbm omnetpp astar xalancbmk ;
    do
      #echo $p$j
      for k in $p$j.o*
      do
        #echo $k
        var=$(cat $k | grep IPC | tr ',' '\n' | tail -1) ;
        #v=$(cat $var | tr ' ' '\n' | tail -1) ;
        #var=$(cat $k | grep IPC | tr ',' '\n' |  sort -n | tail -3) ;
        echo $j $var;
      done
    done
 done
 cd ..
done




#  for j in *.o;#run/*.sh ;
#  do
#    var=$(cat ${j%%.*}.o* | grep IPC   ) ;
    #var=$(cat ${j%%.*}.o* | grep total   ) ;
#    echo $j $var;
#  done
#  cd ..
#done
#for i in perlbench bzip2 gcc bwaves gamess mcf milc zeusmp gromacs cactusADM leslie3d namd gobmk soplex povray calculix hmmer sjeng GemsFDTD libquantum h264ref tonto lbm omnetpp astar xalancbmk ;

