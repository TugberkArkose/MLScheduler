#!/bin/bash
for p in cmp_ EightThreads_;
# pinned fair hrrs;
do
  echo $p;
  for i in barnes cholesky fft fmm lu.cont lu.ncont ocean.cont ocean.ncont radiosity radix raytrace water.nsq water.sp ;
  do
    var=$(cat $p$i/sim.out | grep Time | tr '|' '\n' | tail -4 | sort -n | tail -1) ;
    echo $i $var;
  done
done
