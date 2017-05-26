#!/bin/bash
for p in cmp_;
do
  echo $p;
  for i in perlbench bzip2 gcc bwaves gamess mcf milc zeusmp gromacs cactusADM leslie3d namd gobmk soplex povray calculix hmmer sjeng GemsFDTD libquantum h264ref tonto lbm omnetpp astar xalancbmk ;
  do
    var=$(cat $p$i/sim.out | grep Time | tr '|' '\n' | tail -4 | sort -n | tail -1) ;
    echo $i $var;
  done
done