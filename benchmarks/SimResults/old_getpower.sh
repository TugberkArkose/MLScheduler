#!/bin/bash
for p in hrrs;
do
  echo $p;
  for i in run ;
  do
    var=$(cat $p$i.o* | grep total   ) ;
    echo $i $var;
  done
done

#for i in perlbench bzip2 gcc bwaves gamess mcf milc zeusmp gromacs cactusADM leslie3d namd gobmk soplex povray calculix hmmer sjeng GemsFDTD libquantum h264ref tonto lbm omnetpp astar xalancbmk ;

