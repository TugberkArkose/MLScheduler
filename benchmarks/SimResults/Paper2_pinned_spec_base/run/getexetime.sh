#!/bin/bash
for p in pinned fair tlss hrrs;
do
  echo $p;
  for i in gccbzip2perlbenchbwaves mcfgamessmilczeusmp namdcactusADMgromacsleslie3d soplexgobmkpovraycalculix sjenghmmerGemsFDTDlibquantum omnetpph264reflbmtonto xalancbmkastarleslie3dnamd ;
  do
    var=$(cat $p$i/sim.out | grep Time | tr '|' '\n' | tail -4 | sort -n | tail -1) ;
    echo $i $var;
  done
done